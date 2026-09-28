# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**St. Jude's Bio-Triage Command** — a Streamlit demo that sends patient vitals to TypeSafe **Jev** (a structured "System One" decision model) through the **OpenRouter Decisions API** and visualises the typed decision. It is a sales/education demo, not a clinical tool. `jev_prd.md` is the original spec; the implementation intentionally deviates from it where the PRD was wrong about the API (see below).

## Commands

```bash
uv sync                                   # install deps (.venv)
uv run streamlit run app.py               # run the app (http://localhost:8501)
uv run streamlit run app.py --server.port 8511
uv add <pkg>                              # add a dependency (never pip install)
```

There is no test suite. Verify changes by running the app and, for client changes, a one-off script:

```bash
uv run python -c "from dotenv import load_dotenv; load_dotenv(); import os; from jev_client import query_jev; print(query_jev({'vitals':{'hr':128,'spo2':88,'systolic_bp':175,'temp_c':38.2,'pain_level':9},'intake_summary':'chest pain'}, os.getenv('OPENROUTER_API_KEY')))"
```

`"live": True` means the real API answered; otherwise `"error"` holds the fallback reason.

## Architecture

| File | Responsibility |
|---|---|
| `app.py` | All UI. Header (title + LIVE/SIMULATED pill top-right), tab 1 single-patient, tab 2 batch. |
| `jev_client.py` | `query_jev()` (HTTP + parsing), `fallback_decision()` (local rules), `vital_flags()`, `ACUITY_LEGEND`. **Must not import Streamlit** — it runs inside worker threads. |
| `data.py` | `PRESETS`, `DEFAULT_CASE`, `BATCH_PATIENTS`. |
| `styles.py` | `get_carbon_css()` (copied from the user's `carbon-streamlit` skill template — keep it close to upstream), `DARK_THEME` overrides, `NEON` colours, `get_neon_accents_css()` for demo-specific classes. |
| `.streamlit/config.toml` | Dark base theme matching `DARK_THEME`. |

### Result contract

`query_jev()` and `fallback_decision()` return the **same dict shape**; the UI depends on every key:

```python
{"source", "live", "model", "choice", "confidence",   # confidence is 0-100
 "probs", "acuity_score", "acuity_label", "acuity_probs",
 "latency_ms", "cost_usd", "error"}
```

If you add a field, add it to both functions. `app.py` adds `"cached"` in `triage_cached()`.

### Key behaviours

- **API key** comes only from `.env` (`OPENROUTER_API_KEY`), read via `os.getenv` in `app.py`. There is deliberately no key input in the UI.
- **Caching:** `triage_cached()` stores results in `st.session_state["triage_cache"]` keyed on the JSON payload + key. Only live results (or no-key fallbacks) are cached, so transient failures recover. Don't switch to `st.cache_data` for the batch path — it warns when called off the script thread.
- **Batch:** `ThreadPoolExecutor(max_workers=5)` maps the *uncached* `query_jev`. Results live in `st.session_state["batch_cache"]` as `(results, wall_ms)`.
- **Presets:** the selectbox `on_change` callback writes slider values into `session_state` keys (`v_hr`, `v_spo2`, `v_bp`, `v_temp`, `v_pain`, `v_notes`). Sliders take `key=` only — do not also pass `value=` or Streamlit will warn.
- **Retry:** one retry on `requests.RequestException` (`RETRIES = 1`, `TIMEOUT_S = 8`). Typical latency is ~0.4–0.5 s; occasional tail spikes happen.

## Jev / OpenRouter Decisions API facts (verified live)

- `POST https://openrouter.ai/api/alpha/decisions`, header `Authorization: Bearer <key>`.
- Body: `{model, state, questions}`; model `typesafe/jev-1.13` (response reports a dated id like `typesafe/jev-1.13-20260917`).
- Question types: `choice` (criteria = **dict** label → description), `score` (criteria = **ordered list**; answer `score` is a float 0..N-1 with `probabilities` keyed `"0"`, `"1"`, … and a `legend`), `noul` (boolean; answer `{"noul": p}`).
- `choice` answers: `choice`, `confidence` (0–1), `probabilities`.
- `usage` has `input_tokens`, `output_tokens`, `cost` — **no elapsed time**; latency is measured client-side.
- Errors: 400 bad params, 401 bad key, 402 no credits, 429 rate limit, 5xx provider issues.
- Price ≈ $0.042 / M input tokens, output free → ~$0.00002 per triage call.
- Docs: https://openrouter.ai/docs/guides/community/jev

The PRD's sample code used a dict for `score` criteria and read `usage.elapsedMs`; both are wrong — don't reintroduce them.

## Styling conventions

- IBM Carbon, Gray 100 dark: square corners, IBM Plex Sans / Plex Mono, bg `#161616` / `#262626`, border `#393939`.
- Neon accents only for triage signals: cyan `#00f0ff` (metrics, LIVE), red `#ff3b30` (URGENT, pulsing), green `#34c759` (NON-URGENT), yellow `#f1c21b` (SIMULATED, Moderate).
- New visual classes go in `get_neon_accents_css()`; reuse the `card()` helper and `chart_layout()` in `app.py` for metric cards and Plotly figures.
- Use `width="stretch"` (not the deprecated `use_container_width`) for charts, dataframes and buttons.

## Guardrails

- Never commit `.env` or print the API key. `.env` is gitignored; `.env.example` is the template.
- Keep the "not for clinical use" disclaimer and the LIVE/SIMULATED indicator — the audience must always know whether output is real.
- Vital-sign flags are rule-based context, not Jev's reasoning; keep them labelled as such.
- All patient data is fictional.
