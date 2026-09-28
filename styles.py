"""IBM Carbon Design-inspired CSS styles for Streamlit frontends.

Provides a parameterized theme dict and a CSS generator function.
Override THEME values or pass a custom dict to get_carbon_css() to
customize colors and fonts.
"""

THEME: dict[str, str] = {
    "primary": "#0f62fe",
    "primary_hover": "#0353e9",
    "primary_active": "#002d9c",
    "bg_primary": "#ffffff",
    "bg_secondary": "#f4f4f4",
    "text_primary": "#161616",
    "text_secondary": "#525252",
    "text_helper": "#6f6f6f",
    "text_placeholder": "#a8a8a8",
    "border": "#e0e0e0",
    "success": "#24a148",
    "error": "#da1e28",
    "font_sans": "'IBM Plex Sans', sans-serif",
    "font_mono": "'IBM Plex Mono', monospace",
}


def get_carbon_css(theme: dict[str, str] | None = None) -> str:
    """Return a <style> block with IBM Carbon Design-inspired styles.

    Args:
        theme: Optional dict of theme overrides. Keys should match THEME.
               Missing keys fall back to defaults.
    """
    t = {**THEME, **(theme or {})}
    return f"""
    <style>
    /* IBM Plex fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* Global font override */
    html, body, [class*="css"] {{
        font-family: {t["font_sans"]};
    }}

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Reduce top padding on main content area */
    .stMainBlockContainer {{
        padding-top: 1.5rem !important;
    }}

    /* Logo container - override Streamlit element backgrounds */
    .stMarkdown img {{
        background-color: {t["bg_primary"]} !important;
    }}
    .element-container:has(img) {{
        background: transparent !important;
    }}

    /* Main title */
    h1 {{
        font-family: {t["font_sans"]} !important;
        font-weight: 600 !important;
        color: {t["text_primary"]} !important;
        letter-spacing: -0.02em;
    }}

    /* Subtitle text */
    .subtitle {{
        font-family: {t["font_sans"]};
        font-size: 0.95rem;
        color: {t["text_secondary"]};
        margin-top: -0.8rem;
        margin-bottom: 1.5rem;
    }}

    /* Text input - Carbon underline style */
    .stTextInput > div > div > input {{
        font-family: {t["font_sans"]} !important;
        border: none !important;
        border-bottom: 1px solid {t["border"]} !important;
        border-radius: 0 !important;
        background-color: {t["bg_secondary"]} !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        color: {t["text_primary"]} !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-bottom: 2px solid {t["primary"]} !important;
        box-shadow: none !important;
    }}

    .stTextInput > div > div > input::placeholder {{
        color: {t["text_placeholder"]} !important;
    }}

    /* Submit / Search button - Carbon primary */
    .stFormSubmitButton > button {{
        font-family: {t["font_sans"]} !important;
        background-color: {t["primary"]} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.75rem 2rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        text-transform: none !important;
        min-height: 2.5rem !important;
    }}

    .stFormSubmitButton > button:hover {{
        background-color: {t["primary_hover"]} !important;
    }}

    .stFormSubmitButton > button:active {{
        background-color: {t["primary_active"]} !important;
    }}

    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: {t["bg_secondary"]} !important;
        border-right: 1px solid {t["border"]};
    }}

    section[data-testid="stSidebar"] h2 {{
        font-family: {t["font_sans"]} !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: {t["text_secondary"]} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-bottom: 0.75rem;
    }}

    /* Tool card */
    .tool-card {{
        background-color: {t["bg_primary"]};
        border: 1px solid {t["border"]};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }}

    .tool-card .tool-name {{
        font-family: {t["font_mono"]};
        font-size: 0.8rem;
        font-weight: 500;
        color: {t["primary"]};
        margin-bottom: 0.35rem;
    }}

    .tool-card .tool-args {{
        font-family: {t["font_sans"]};
        font-size: 0.75rem;
        color: {t["text_secondary"]};
        line-height: 1.4;
    }}

    .tool-card .tool-args .arg-key {{
        color: {t["text_helper"]};
    }}

    /* Skill card - distinct from tool cards with blue accent */
    .skill-card {{
        background: linear-gradient(135deg, #e8f4fd 0%, #ffffff 100%);
        border: 1px solid {t["border"]};
        border-left: 3px solid {t["primary"]};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }}

    .skill-card .skill-name {{
        font-family: {t["font_sans"]};
        font-size: 0.85rem;
        font-weight: 600;
        color: {t["primary"]};
        margin-bottom: 0.35rem;
    }}

    .skill-card .skill-desc {{
        font-family: {t["font_sans"]};
        font-size: 0.75rem;
        color: {t["text_secondary"]};
        line-height: 1.4;
    }}

    /* Sidebar ghost button */
    section[data-testid="stSidebar"] .stButton > button {{
        font-family: {t["font_sans"]} !important;
        background-color: transparent !important;
        color: {t["primary"]} !important;
        border: 1px solid {t["primary"]} !important;
        border-radius: 0 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        width: 100%;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {t["primary"]} !important;
        color: #ffffff !important;
    }}

    /* Health indicator */
    .health-indicator {{
        font-family: {t["font_sans"]};
        font-size: 0.75rem;
        color: {t["text_helper"]};
        padding: 0.5rem 0;
    }}

    .health-indicator .dot-ok {{
        color: {t["success"]};
    }}

    .health-indicator .dot-err {{
        color: {t["error"]};
    }}

    /* Empty state */
    .empty-state {{
        text-align: center;
        padding: 3rem 1rem;
    }}

    .empty-state .empty-title {{
        font-family: {t["font_sans"]};
        font-size: 1.1rem;
        font-weight: 500;
        color: {t["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .empty-state .empty-desc {{
        font-family: {t["font_sans"]};
        font-size: 0.875rem;
        color: {t["text_secondary"]};
        margin-bottom: 1.5rem;
    }}

    .empty-state .example-query {{
        font-family: {t["font_sans"]};
        font-size: 0.8rem;
        color: {t["text_helper"]};
        background-color: {t["bg_secondary"]};
        padding: 0.4rem 0.75rem;
        margin: 0.25rem auto;
        display: inline-block;
        border-left: 2px solid {t["primary"]};
    }}

    /* Markdown content in main area */
    .stMarkdown {{
        font-family: {t["font_sans"]} !important;
        color: {t["text_secondary"]};
        line-height: 1.6;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {t["border"]};
        margin: 1rem 0;
    }}
    </style>
    """


# Carbon Gray 100 (dark) theme overrides for the triage command dashboard.
DARK_THEME: dict[str, str] = {
    "primary": "#4589ff",
    "primary_hover": "#0f62fe",
    "primary_active": "#0043ce",
    "bg_primary": "#161616",
    "bg_secondary": "#262626",
    "text_primary": "#f4f4f4",
    "text_secondary": "#c6c6c6",
    "text_helper": "#8d8d8d",
    "text_placeholder": "#6f6f6f",
    "border": "#393939",
    "success": "#42be65",
    "error": "#fa4d56",
}

NEON = {"cyan": "#00f0ff", "red": "#ff3b30", "green": "#34c759"}


def get_neon_accents_css(theme: dict[str, str] | None = None) -> str:
    """Return the neon triage accents (pulsing badges, metric cards) layered on Carbon."""
    t = {**THEME, **DARK_THEME, **(theme or {})}
    return f"""
    <style>
    .stMainBlockContainer {{
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 100% !important;
    }}

    h3, h4, h5 {{
        font-family: {t["font_sans"]} !important;
        color: {t["text_primary"]} !important;
    }}

    .section-label {{
        font-family: {t["font_mono"]};
        font-size: 0.72rem;
        color: {t["text_helper"]};
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border-bottom: 1px solid {t["border"]};
        padding-bottom: 0.35rem;
        margin-bottom: 0.75rem;
    }}

    /* Metric card */
    .stCard {{
        background-color: {t["bg_secondary"]};
        border: 1px solid {t["border"]};
        border-top: 2px solid {NEON["cyan"]};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }}
    .metric-value {{
        font-family: {t["font_mono"]};
        font-size: 1.5rem;
        font-weight: 500;
        color: {NEON["cyan"]};
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.35);
    }}
    .metric-label {{
        font-family: {t["font_sans"]};
        font-size: 0.7rem;
        color: {t["text_helper"]};
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    .metric-sub {{
        font-family: {t["font_sans"]};
        font-size: 0.75rem;
        color: {t["text_secondary"]};
    }}

    /* Triage badges */
    .triage-badge {{
        font-family: {t["font_sans"]};
        font-size: 1.35rem;
        font-weight: 600;
        text-align: center;
        padding: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }}
    .urgent-badge {{
        background: rgba(255, 59, 48, 0.15);
        color: {NEON["red"]};
        border: 2px solid {NEON["red"]};
        animation: pulse-red 1.5s infinite;
    }}
    .non-urgent-badge {{
        background: rgba(52, 199, 89, 0.15);
        color: {NEON["green"]};
        border: 2px solid {NEON["green"]};
        box-shadow: 0 0 15px rgba(52, 199, 89, 0.3);
    }}
    @keyframes pulse-red {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); }}
        70% {{ box-shadow: 0 0 0 12px rgba(255, 59, 48, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }}
    }}

    /* LIVE / SIMULATED engine status pill */
    .status-pill {{
        display: inline-block;
        font-family: {t["font_mono"]};
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        padding: 0.25rem 0.6rem;
        border: 1px solid;
        margin-top: 0.3rem;
    }}
    .status-live {{
        color: {NEON["cyan"]};
        border-color: {NEON["cyan"]};
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.35);
    }}
    .status-sim {{
        color: #f1c21b;
        border-color: #f1c21b;
    }}
    .status-corner {{
        text-align: right;
        padding-top: 0.6rem;
    }}
    .status-reason {{
        font-size: 0.72rem;
        color: {t["text_helper"]};
        margin-top: 0.25rem;
    }}

    /* Tabs - Carbon line tabs */
    .stTabs [data-baseweb="tab"] {{
        font-family: {t["font_sans"]};
        border-radius: 0 !important;
    }}

    /* Primary buttons - square Carbon corners */
    .stButton > button {{
        border-radius: 0 !important;
        font-family: {t["font_sans"]} !important;
    }}

    .disclaimer {{
        font-size: 0.72rem;
        color: {t["text_helper"]};
        text-align: center;
        margin-top: 1.5rem;
    }}
    </style>
    """
