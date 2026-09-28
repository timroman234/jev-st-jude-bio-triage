"""TypeSafe Jev decision client (OpenRouter Decisions API) with a local fallback.

Kept free of Streamlit imports so it can be called from worker threads.
"""

import time

import requests

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
TIMEOUT_S = 8
RETRIES = 1  # one retry on network errors/timeouts; typical latency is ~0.4s

ACUITY_LEGEND = [
    "Stable: vitals within normal physiological boundaries",
    "Moderate: single abnormality or moderate discomfort",
    "Critical: multi-organ risk, severe respiratory distress, or hemodynamic instability",
]

HTTP_ERRORS = {
    400: "Invalid request parameters",
    401: "Invalid or missing API key",
    402: "Insufficient OpenRouter credits",
    429: "Rate limit exceeded",
    502: "Provider returned error",
    503: "Service temporarily unavailable",
    524: "Request timed out",
}


def build_questions() -> dict:
    return {
        "urgency": {
            "type": "choice",
            "instructions": "Classify if patient requires immediate critical intervention or standard care.",
            "criteria": {
                "URGENT": "Life-threatening vitals (SpO2 < 92, HR > 120, severe pain, sepsis symptoms, stroke symptoms)",
                "NON_URGENT": "Stable vitals, minor aches, mild rashes, routine symptom checks",
            },
        },
        "acuity_score": {
            "type": "score",
            "instructions": "Grade the clinical severity level on a rubric.",
            "criteria": ACUITY_LEGEND,
        },
    }


def _acuity_label(score: float) -> str:
    idx = min(max(round(score), 0), len(ACUITY_LEGEND) - 1)
    return ACUITY_LEGEND[idx].split(":")[0]


def query_jev(payload: dict, api_key: str | None) -> dict:
    """Ask Jev to triage one patient. Falls back to a local heuristic on any failure."""
    if not api_key or not api_key.strip():
        return fallback_decision(payload, "No API key provided")

    body = {"model": JEV_MODEL, "state": payload, "questions": build_questions()}
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}

    for attempt in range(1 + RETRIES):
        t0 = time.perf_counter()
        try:
            resp = requests.post(JEV_URL, headers=headers, json=body, timeout=TIMEOUT_S)
            break
        except requests.RequestException as exc:
            if attempt == RETRIES:
                return fallback_decision(payload, f"Network error: {type(exc).__name__}")
    latency_ms = round((time.perf_counter() - t0) * 1000)

    if resp.status_code != 200:
        reason = HTTP_ERRORS.get(resp.status_code, "Unexpected error")
        return fallback_decision(payload, f"HTTP {resp.status_code}: {reason}")

    try:
        data = resp.json()
        answers = data["answers"]
        urg = answers["urgency"]
        acu = answers.get("acuity_score", {})
        probs = urg.get("probabilities") or {urg["choice"]: 1.0}
        score = float(acu.get("score", 0.0))
        return {
            "source": "Jev via OpenRouter",
            "live": True,
            "model": data.get("model", JEV_MODEL),
            "choice": urg["choice"],
            "confidence": round(float(urg.get("confidence", max(probs.values()))) * 100, 1),
            "probs": {k: float(v) for k, v in probs.items()},
            "acuity_score": round(score, 2),
            "acuity_label": _acuity_label(score),
            "acuity_probs": {k: float(v) for k, v in (acu.get("probabilities") or {}).items()},
            "latency_ms": latency_ms,
            "cost_usd": data.get("usage", {}).get("cost"),
            "error": None,
        }
    except (ValueError, KeyError, TypeError) as exc:
        return fallback_decision(payload, f"Unparseable response: {type(exc).__name__}")


def fallback_decision(payload: dict, error: str | None = None) -> dict:
    """Rule-based stand-in used when the Jev API is unavailable."""
    t0 = time.perf_counter()
    v = payload["vitals"]
    spo2, hr, bp, pain = v["spo2"], v["hr"], v["systolic_bp"], v["pain_level"]

    flags = sum([spo2 < 92, hr > 115, bp > 160 or bp < 95, pain >= 8])
    is_urgent = flags > 0
    p_urgent = 0.96 if is_urgent else 0.05
    score = 2.0 if flags >= 2 else float(flags)

    return {
        "source": "Simulated Jev (fallback)",
        "live": False,
        "model": "local-heuristic",
        "choice": "URGENT" if is_urgent else "NON_URGENT",
        "confidence": round((p_urgent if is_urgent else 1 - p_urgent) * 100, 1),
        "probs": {"URGENT": p_urgent, "NON_URGENT": round(1 - p_urgent, 2)},
        "acuity_score": score,
        "acuity_label": _acuity_label(score),
        "acuity_probs": {str(i): 1.0 if i == int(score) else 0.0 for i in range(len(ACUITY_LEGEND))},
        "latency_ms": max(1, round((time.perf_counter() - t0) * 1000)),
        "cost_usd": 0.0,
        "error": error,
    }


def vital_flags(hr: int, spo2: int, bp: int, pain: int) -> list[str]:
    """Rule-based vital-sign flags shown alongside Jev's decision."""
    flags = []
    if spo2 < 92:
        flags.append(f"⚠️ **Hypoxia risk**: SpO2 at {spo2}%")
    if hr > 115:
        flags.append(f"⚠️ **Tachycardia**: heart rate {hr} BPM")
    if bp > 160 or bp < 95:
        flags.append(f"⚠️ **BP alert**: systolic at {bp} mmHg")
    if pain >= 8:
        flags.append(f"⚠️ **Acute pain**: index {pain}/10")
    return flags or ["✅ All vital signs within standard limits."]
