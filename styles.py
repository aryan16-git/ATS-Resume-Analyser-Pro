"""
styles.py
High-contrast editorial dark design system for ATS Resume Analyser PRO.

Design language:
- Matte near-black surfaces, not pure black -- avoids the "OLED void" look.
- Serif display type (Fraunces) for headlines -- gives it an editorial,
  magazine-report feel instead of generic SaaS. Inter for body/UI text.
- One disciplined accent color used sparingly (amber), not gradients.
- Sharp 1-2px borders instead of soft drop shadows and rounded blobs.
- Plenty of negative space; no boxed-in cards for every single element.
"""

import streamlit as st
import plotly.graph_objects as go


# ============ DESIGN TOKENS ============

COLORS = {
    "bg": "#0c0c0b",
    "surface": "#161615",
    "surface_alt": "#1e1e1c",
    "border": "#2e2e2b",
    "border_strong": "#45453f",
    "text": "#f2f1ea",
    "text_muted": "#9a988f",
    "accent": "#e8a33d",       # warm amber -- the ONE accent color
    "accent_dim": "#8a6a2f",
    "success": "#7fb069",
    "warning": "#e8a33d",
    "danger": "#c1554d",
}


# ============ CSS INJECTION ============

def inject_custom_css():
    """Call once near the top of app.py, right after st.set_page_config()."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

    :root {{
        --bg: {COLORS['bg']};
        --surface: {COLORS['surface']};
        --surface-alt: {COLORS['surface_alt']};
        --border: {COLORS['border']};
        --border-strong: {COLORS['border_strong']};
        --text: {COLORS['text']};
        --text-muted: {COLORS['text_muted']};
        --accent: {COLORS['accent']};
        --success: {COLORS['success']};
        --danger: {COLORS['danger']};
    }}

    /* ===== BASE ===== */
    .stApp {{
        background-color: var(--bg);
        color: var(--text);
    }}
    .block-container {{
        padding-top: 2rem !important;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    h1, h2, h3 {{
        font-family: 'Fraunces', Georgia, serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
        color: var(--text) !important;
    }}

    h1 {{ font-size: 2.75rem !important; }}
    h2 {{ font-size: 1.85rem !important; }}
    h3 {{ font-size: 1.3rem !important; }}

    p, span, div, label {{
        color: var(--text);
    }}

    /* ===== MASTHEAD (replaces the old purple gradient header) ===== */
    .masthead {{
        border-bottom: 2px solid var(--border-strong);
        padding: 2rem 0 1.5rem 0;
        margin-bottom: 3rem;
    }}
    .masthead .eyebrow {{
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-size: 0.75rem;
        color: var(--accent);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    .masthead h1 {{
        margin: 0 0 0.4rem 0 !important;
    }}
    .masthead .subtitle {{
        color: var(--text-muted);
        font-size: 1rem;
        max-width: 640px;
    }}

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border);
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--text) !important;
    }}
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] textarea {{
        background-color: var(--bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
    }}

    /* ===== BUTTONS: flat, sharp, no gradients ===== */
    .stButton > button {{
        background-color: transparent !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 3px !important;
        padding: 0.55rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em;
        white-space: nowrap !important;
        transition: background-color 0.15s ease, color 0.15s ease !important;
        box-shadow: none !important;
    }}
    .stButton > button:hover {{
        background-color: var(--accent) !important;
        color: var(--bg) !important;
        border-color: var(--accent) !important;
    }}
    .stFormSubmitButton > button {{
        background-color: var(--accent) !important;
        color: var(--bg) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 3px !important;
        font-weight: 600 !important;
    }}
    .stFormSubmitButton > button:hover {{
        background-color: transparent !important;
        color: var(--accent) !important;
    }}

    /* ===== TABS: underline style, no rounded pill boxes ===== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        border-bottom: 1px solid var(--border);
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 0;
        padding: 10px 16px;
        color: var(--text-muted);
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }}

    /* ===== INPUTS ===== */
    .stTextArea textarea, .stTextInput input {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }}

    [data-testid="stFileUploader"] {{
        border: 1px dashed var(--border-strong);
        border-radius: 4px;
        background-color: var(--surface);
        padding: 1.25rem;
    }}

    /* ===== METRIC CARDS: flat surfaces, sharp left rule, no shadows ===== */
    .stat-card {{
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 2px;
        padding: 1.25rem 1.5rem;
    }}
    .stat-card .stat-label {{
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.72rem;
        color: var(--text-muted);
        font-weight: 600;
        margin-bottom: 0.4rem;
    }}
    .stat-card .stat-value {{
        font-family: 'Fraunces', serif;
        font-size: 2.2rem;
        font-weight: 600;
        line-height: 1;
        color: var(--text);
    }}
    .stat-card .stat-value.accent {{ color: var(--accent); }}
    .stat-card .stat-value.success {{ color: var(--success); }}
    .stat-card .stat-value.danger {{ color: var(--danger); }}
    .stat-card .stat-sub {{
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }}

    /* ===== ALERTS: flatten Streamlit's default rounded/colored boxes ===== */
    .stAlert {{
        border-radius: 3px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
    }}

    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 3px !important;
        color: var(--text) !important;
    }}

    /* ===== SKELETON LOADER ===== */
    @keyframes shimmer {{
        0% {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}
    .skeleton-block {{
        height: 1rem;
        border-radius: 3px;
        margin-bottom: 0.6rem;
        background: linear-gradient(90deg, var(--surface) 25%, var(--surface-alt) 50%, var(--surface) 75%);
        background-size: 800px 100%;
        animation: shimmer 1.4s infinite linear;
    }}

    /* ===== TOP TOOLBAR: this is Streamlit's built-in Deploy/menu bar.
       We deploy via git push to Streamlit Cloud, not this button, so
       it serves no purpose here. Streamlit renamed this element's
       test-id across versions (stToolbar -> stAppDeployButton in
       1.38), so we match both rather than relying on one. IMPORTANT:
       the sidebar's own open/close control is a DIFFERENT element and
       is NOT touched by this rule. ===== */
    header[data-testid="stHeader"] {{
        background-color: var(--bg) !important;
    }}
    [data-testid="stToolbar"],
    [data-testid="stAppDeployButton"],
    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}
    [data-testid="stDecoration"] {{
        background-image: none !important;
        background-color: var(--accent) !important;
    }}

    /* ===== SIDEBAR OPEN/CLOSE CONTROL ===== */
    /* Streamlit's native collapse control is hidden entirely -- see
       app.py, which drives sidebar visibility with a custom toggle
       button instead, since the native control's internal test-ids
       and behavior proved unreliable to restyle across versions. */

    /* ===== SELECT BOXES (model picker, etc.) ===== */
    div[data-baseweb="select"] {{
        background-color: var(--surface) !important;
    }}
    div[data-baseweb="select"] div {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: var(--text) !important;
    }}
    /* The dropdown menu is portaled to <body>, outside .stApp. Its
       exact internal nesting (menu/list/option) varies by Streamlit
       version, so instead of guessing the structure we recolor
       everything inside the popover wholesale, then restyle text and
       hover state on top. */
    div[data-baseweb="popover"] * {{
        background-color: var(--surface) !important;
    }}
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"] {{
        color: var(--text) !important;
    }}
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [aria-selected="true"] {{
        background-color: var(--surface-alt) !important;
    }}

    /* ===== DOWNLOAD BUTTON (separate widget class from st.button) ===== */
    .stDownloadButton > button {{
        background-color: transparent !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 3px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: var(--accent) !important;
        color: var(--bg) !important;
    }}
    .stDownloadButton > button p {{
        color: inherit !important;
    }}

    /* ===== PASSWORD INPUT: the native "Press Enter to submit" hint
       overlaps the eye-toggle icon no matter how it's colored -- it's
       a positioning collision, not a contrast issue. Hide the hint
       entirely; the form still submits on Enter regardless. ===== */
    .stTextInput input[type="password"] {{
        padding-right: 2.75rem !important;
    }}
    [data-testid="InputInstructions"] {{
        display: none !important;
    }}

    /* ===== SIDEBAR: keep it above chart canvases when collapsing/expanding ===== */
    section[data-testid="stSidebar"] {{
        z-index: 999 !important;
    }}

    /* ===== STAT CARD VALUE: long filenames truncate cleanly instead of
       clipping mid-character ===== */
    .stat-card .stat-value {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Hide Streamlit chrome we don't want */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


# ============ REUSABLE UI COMPONENTS ============

def render_masthead(eyebrow: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="masthead">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label: str, value: str, sub: str = "", tone: str = "default"):
    """tone: 'default' | 'accent' | 'success' | 'danger'"""
    tone_class = "" if tone == "default" else tone
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value {tone_class}">{value}</div>
        <div class="stat-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def render_skeleton_loader(lines: int = 4):
    """Show while an AI analysis is in-flight, instead of a blank spinner."""
    widths = [90, 75, 85, 60]
    blocks = "".join(
        '<div class="skeleton-block" style="width:' + str(w) + '%"></div>'
        for w in widths[:lines]
    )
    st.markdown('<div>' + blocks + '</div>', unsafe_allow_html=True)


# ============ PLOTLY THEMING ============

def create_gauge_chart(score: int, title: str = "ATS Score") -> go.Figure:
    """
    Minimal monochrome gauge. Bar color shifts by score band so a FAIL
    reads as clearly red, not just amber-adjacent:
      >= 70  -> success green
      40-69  -> amber accent
      < 40   -> danger red
    """
    if score >= 70:
        bar_color = COLORS["success"]
    elif score >= 40:
        bar_color = COLORS["accent"]
    else:
        bar_color = COLORS["danger"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"size": 56, "color": COLORS["text"], "family": "Fraunces"}},
        title={"text": title, "font": {"size": 14, "color": COLORS["text_muted"], "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["border"], "tickfont": {"color": COLORS["border"], "size": 1}, "showticklabels": False},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": COLORS["surface"],
            "borderwidth": 1,
            "bordercolor": COLORS["border"],
            "steps": [{"range": [0, 100], "color": COLORS["surface"]}],
        },
    ))
    fig.update_layout(
        height=280,
        width=420,
        autosize=False,
        margin=dict(l=30, r=30, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"]},
    )
    return fig


def create_radar_chart(scores_dict: dict, title: str = "Breakdown") -> go.Figure:
    """Single monochrome trace, no fill gradient, thin grid."""
    categories = [k.replace("_", " ").title() for k in scores_dict.keys()]
    values = list(scores_dict.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(232, 163, 61, 0.12)",
        line=dict(color=COLORS["accent"], width=2),
        marker=dict(size=5, color=COLORS["accent"]),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor=COLORS["border"], linecolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"], size=9),
            ),
            angularaxis=dict(
                gridcolor=COLORS["border"], linecolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"], size=11),
            ),
        ),
        showlegend=False,
        title=dict(text=title, font=dict(size=14, color=COLORS["text_muted"], family="Inter")),
        height=350,
        margin=dict(l=90, r=90, t=60, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig