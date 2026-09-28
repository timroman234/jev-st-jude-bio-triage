import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from data import BATCH_PATIENTS, DEFAULT_CASE, PRESETS
from jev_client import ACUITY_LEGEND, query_jev, vital_flags
from styles import DARK_THEME, NEON, get_carbon_css, get_neon_accents_css

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="St. Jude's Bio-Triage Command",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(get_carbon_css(DARK_THEME), unsafe_allow_html=True)
st.markdown(get_neon_accents_css(), unsafe_allow_html=True)

CHART_FONT = dict(family="IBM Plex Sans, sans-serif", color=DARK_THEME["text_secondary"], size=12)
ACUITY_NAMES = [label.split(":")[0] for label in ACUITY_LEGEND]


def chart_layout(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=CHART_FONT,
        showlegend=False,
    )
    return fig


def card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f'<div class="stCard"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{sub_html}</div>'


def to_payload(hr, spo2, bp, temp, pain, notes) -> dict:
    return {
        "vitals": {"hr": hr, "spo2": spo2, "systolic_bp": bp, "temp_c": temp, "pain_level": pain},
        "intake_summary": notes,
    }


def triage_cached(payload: dict, api_key: str) -> dict:
    """Per-session cache so revisiting an identical vitals state costs nothing.

    Transient failures (rate limits, network) are not cached so they can recover.
    """
    cache = st.session_state.setdefault("triage_cache", {})
    cache_key = (json.dumps(payload, sort_keys=True), api_key)
    if cache_key in cache:
        return {**cache[cache_key], "cached": True}
    result = query_jev(payload, api_key)
    if result["live"] or not api_key:
        cache[cache_key] = result
    return {**result, "cached": False}


# --- Slider state & preset loading ---
def apply_case(case: dict) -> None:
    st.session_state.update(
        v_hr=case["hr"], v_spo2=case["spo2"], v_bp=case["bp_sys"],
        v_temp=float(case["temp"]), v_pain=case["pain"], v_notes=case["notes"],
    )


def on_preset_change() -> None:
    case = PRESETS.get(st.session_state["preset"])
    if case:
        apply_case(case)


if "v_hr" not in st.session_state:
    apply_case(DEFAULT_CASE)

# --- Header Banner ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("### 🏥 St. Jude's Memorial Hospital — Bio-Triage Decision Engine")
    st.caption("Powered by **TypeSafe Jev** · System One rapid classification via OpenRouter Decisions API")
with col_head2:
    status_slot = st.empty()

api_key = os.getenv("OPENROUTER_API_KEY", "")


def render_status(result: dict) -> None:
    if result["live"]:
        pill = f'<span class="status-pill status-live">● LIVE · {result["model"]}</span>'
        reason = ""
    else:
        pill = '<span class="status-pill status-sim">● SIMULATED · local heuristic</span>'
        reason = f'<div class="status-reason">Fallback reason: {result["error"]}</div>' if result["error"] else ""
    status_slot.markdown(f'<div class="status-corner">{pill}{reason}</div>', unsafe_allow_html=True)


# --- Application Tabs ---
tab_single, tab_batch = st.tabs(["👤 Live Single-Patient Triage", "⚡ Batch Queue Triage (5 Patients)"])

# ==================== TAB 1: SINGLE PATIENT TRIAGE ====================
with tab_single:
    col_vitals, col_decision, col_analytics = st.columns([1.1, 1, 1.2], gap="large")

    with col_vitals:
        st.markdown('<div class="section-label">01 · Patient Vitals Simulator</div>', unsafe_allow_html=True)
        st.selectbox("Quick load case study", list(PRESETS.keys()), key="preset", on_change=on_preset_change)
        v_hr = st.slider("Heart Rate (BPM)", 40, 180, key="v_hr")
        v_spo2 = st.slider("Oxygen Saturation (SpO2 %)", 70, 100, key="v_spo2")
        v_bp = st.slider("Systolic BP (mmHg)", 70, 210, key="v_bp")
        v_temp = st.slider("Temperature (°C)", 35.0, 41.0, step=0.1, format="%.1f", key="v_temp")
        v_pain = st.slider("Pain Index (0-10)", 0, 10, key="v_pain")
        v_notes = st.text_area("Clinical intake notes", height=80, key="v_notes")

    payload = to_payload(v_hr, v_spo2, v_bp, round(v_temp, 1), v_pain, v_notes)
    result = triage_cached(payload, api_key)
    render_status(result)

    with col_decision:
        st.markdown('<div class="section-label">02 · Jev System One Choice</div>', unsafe_allow_html=True)
        choice, conf = result["choice"], result["confidence"]
        is_urgent = choice == "URGENT"

        if is_urgent:
            st.markdown('<div class="triage-badge urgent-badge">🚨 Critical: Urgent</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="triage-badge non-urgent-badge">✅ Stable: Non-Urgent</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        latency_sub = "cache hit · $0" if result["cached"] else ("round trip" if result["live"] else "local")
        c1.markdown(card("Confidence", f"{conf}%"), unsafe_allow_html=True)
        c2.markdown(card("Inference Time", f"{result['latency_ms']} ms", latency_sub), unsafe_allow_html=True)

        bar_color = NEON["red"] if is_urgent else NEON["cyan"]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conf,
            number={"suffix": "%", "font": {"color": bar_color, "size": 28, "family": "IBM Plex Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": DARK_THEME["border"]},
                "bar": {"color": bar_color},
                "bgcolor": DARK_THEME["bg_secondary"],
                "borderwidth": 1,
                "bordercolor": DARK_THEME["border"],
            },
        ))
        chart_layout(fig_gauge, 180).update_layout(margin=dict(l=30, r=30, t=20, b=10))
        st.plotly_chart(fig_gauge, width="stretch", config={"displayModeBar": False})

        cost = result.get("cost_usd")
        if result["live"] and cost is not None:
            st.caption(f"Call cost: ${cost:.8f} · model `{result['model']}`")

    with col_analytics:
        st.markdown('<div class="section-label">03 · Decision Breakdown</div>', unsafe_allow_html=True)
        probs = result["probs"]
        cats = list(probs.keys())
        vals = [round(v * 100, 1) for v in probs.values()]
        fig_bar = go.Figure(go.Bar(
            x=vals, y=cats, orientation="h",
            marker=dict(color=[NEON["red"] if c == "URGENT" else NEON["green"] for c in cats]),
            text=[f"{v}%" for v in vals], textposition="auto",
        ))
        fig_bar.update_xaxes(visible=False, range=[0, 100])
        st.plotly_chart(chart_layout(fig_bar, 110), width="stretch", config={"displayModeBar": False})

        score = result["acuity_score"]
        st.markdown(
            card("Acuity Score (0–2)", f"{score:.2f}", result["acuity_label"]),
            unsafe_allow_html=True,
        )
        acuity_probs = result["acuity_probs"]
        if acuity_probs:
            a_vals = [round(acuity_probs.get(str(i), 0.0) * 100, 1) for i in range(len(ACUITY_NAMES))]
            fig_acu = go.Figure(go.Bar(
                x=ACUITY_NAMES, y=a_vals,
                marker=dict(color=[NEON["green"], "#f1c21b", NEON["red"]]),
                text=[f"{v}%" for v in a_vals], textposition="outside", cliponaxis=False,
            ))
            fig_acu.update_yaxes(visible=False, range=[0, 115])
            st.plotly_chart(chart_layout(fig_acu, 140), width="stretch", config={"displayModeBar": False})

        st.markdown("**Vital-sign flags** <span style='font-size:0.72rem;color:#8d8d8d'>(rule-based, for context)</span>", unsafe_allow_html=True)
        for flag in vital_flags(v_hr, v_spo2, v_bp, v_pain):
            st.markdown(f"- {flag}")

# ==================== TAB 2: BATCH QUEUE PROCESSING ====================
with tab_batch:
    col_b1, col_b2 = st.columns([2.5, 1])
    with col_b1:
        st.markdown("#### Emergency Waiting Queue (Simultaneous Evaluation)")
    with col_b2:
        run_batch = st.button("🚀 Evaluate 5-Patient Batch with Jev", width="stretch", type="primary")

    if run_batch:
        with st.spinner("Dispatching all 5 patients to Jev in parallel..."):
            payloads = [to_payload(p["hr"], p["spo2"], p["bp"], p["temp"], p["pain"], p["notes"]) for p in BATCH_PATIENTS]
            t_start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=len(payloads)) as pool:
                results = list(pool.map(lambda pl: query_jev(pl, api_key), payloads))
            wall_ms = round((time.perf_counter() - t_start) * 1000)
        st.session_state["batch_cache"] = ([{**p, **r} for p, r in zip(BATCH_PATIENTS, results)], wall_ms)

    if "batch_cache" in st.session_state:
        batch_results, wall_ms = st.session_state["batch_cache"]
        batch_results = sorted(batch_results, key=lambda r: (r["choice"] != "URGENT", -r["acuity_score"]))
        u_count = sum(1 for r in batch_results if r["choice"] == "URGENT")
        summed_ms = sum(r["latency_ms"] for r in batch_results)
        live_count = sum(1 for r in batch_results if r["live"])
        total_cost = sum(r.get("cost_usd") or 0 for r in batch_results)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(card("Total Patients", str(len(batch_results)), f"{live_count} live · {len(batch_results) - live_count} simulated"), unsafe_allow_html=True)
        m2.markdown(card("Urgent Cases", str(u_count), "prioritised to top"), unsafe_allow_html=True)
        m3.markdown(card("Non-Urgent", str(len(batch_results) - u_count)), unsafe_allow_html=True)
        m4.markdown(card("Batch Wall Time", f"{wall_ms} ms", f"vs {summed_ms} ms sequential"), unsafe_allow_html=True)
        m5.markdown(card("Batch Cost", f"${total_cost:.6f}"), unsafe_allow_html=True)

        errors = {r["error"] for r in batch_results if r["error"]}
        if errors:
            st.warning("Some patients used the simulated fallback: " + "; ".join(sorted(errors)))

        df = pd.DataFrame([
            {
                "Priority": i + 1,
                "ID": r["id"],
                "Patient Name": r["name"],
                "Age": r["age"],
                "HR": f"{r['hr']} bpm",
                "SpO2": f"{r['spo2']}%",
                "BP": f"{r['bp']} mmHg",
                "Jev Decision": "🚨 URGENT" if r["choice"] == "URGENT" else "✅ NON_URGENT",
                "Confidence": f"{r['confidence']}%",
                "Acuity": f"{r['acuity_score']:.2f} · {r['acuity_label']}",
                "Latency": f"{r['latency_ms']} ms",
            }
            for i, r in enumerate(batch_results)
        ])
        st.dataframe(df, width="stretch", hide_index=True)

        st.markdown("##### Individual Patient Jev Diagnostics")
        c_p1, c_p2 = st.columns(2)
        for idx, r in enumerate(batch_results):
            with (c_p1 if idx % 2 == 0 else c_p2):
                with st.expander(f"{'🚨' if r['choice'] == 'URGENT' else '✅'} {r['id']} - {r['name']} ({r['choice']})"):
                    st.write(f"**Notes:** {r['notes']}")
                    st.write(f"**Vitals:** HR {r['hr']} | SpO2 {r['spo2']}% | BP {r['bp']} | Temp {r['temp']}°C | Pain {r['pain']}/10")
                    st.write(f"**Confidence:** {r['confidence']}% | **Acuity:** {r['acuity_score']:.2f} ({r['acuity_label']}) | **Latency:** {r['latency_ms']} ms")
                    st.caption(f"Source: {r['source']}" + (f" · {r['error']}" if r["error"] else ""))
    else:
        st.info("Click 'Evaluate 5-Patient Batch with Jev' above to classify the whole waiting queue simultaneously.")

st.markdown('<div class="disclaimer">Demonstration only — not a medical device and not for clinical use.</div>', unsafe_allow_html=True)
