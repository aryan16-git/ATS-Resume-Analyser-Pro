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

import re

import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF


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


import unicodedata


def _pdf_safe(text) -> str:
    """
    FPDF's core fonts (Helvetica) only support latin-1. Model output
    commonly contains Unicode punctuation and spacing latin-1 can't
    represent -- em/en dashes, smart quotes, bullets, and various
    "typographic" space characters (narrow no-break space, thin space,
    etc. -- there are ~20 of these, not just the common nbsp).

    Rather than hardcode every individual character (which will always
    miss the next one the model uses), we handle known punctuation
    explicitly for correctness, then classify anything else by Unicode
    category: space-separator chars become a regular space, invisible
    format/combining marks are dropped silently, and only genuinely
    unrepresentable characters (e.g. CJK) fall back to '?'.
    """
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u2010": "-",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2022": " | ", "\u2026": "...", "\u2192": "->",
        "\u2265": ">=", "\u2264": "<=", "\u2260": "!=", "\u00b1": "+/-",
        "\u2248": "~", "\u223c": "~", "\uff5e": "~",
    }
    s = str(text)
    for bad, good in replacements.items():
        s = s.replace(bad, good)

    cleaned_chars = []
    for ch in s:
        if ord(ch) < 256:
            cleaned_chars.append(ch)
            continue
        category = unicodedata.category(ch)
        if category == "Zs":  # any Unicode space separator variant
            cleaned_chars.append(" ")
        elif category in ("Cf", "Mn"):  # zero-width/format/combining marks
            continue
        else:
            cleaned_chars.append(ch)  # let latin-1 encode below decide
    s = "".join(cleaned_chars)

    return s.encode("latin-1", "replace").decode("latin-1")


def _strip_md_inline(text: str) -> str:
    """Remove inline markdown markup (bold/italic/code) and return plain text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def _render_md_table(pdf: FPDF, table_lines: list):
    """
    Render a markdown pipe-table as an actual bordered grid with proper
    text wrapping -- NOT truncation. An earlier version cut long cell
    text off mid-word past a fixed character count, silently losing
    content. This version measures wrapped line count per cell first
    (dry run), pads shorter cells with blank lines so every cell in a
    row shares the same box height, then draws the row for real.
    """
    rows = []
    for line in table_lines:
        line = line.strip().strip("|")
        cells = [c.strip() for c in line.split("|")]
        if all(set(c) <= set("-: ") for c in cells if c) and any(c for c in cells):
            continue  # skip the "---|---|---" separator row
        rows.append(cells)
    if not rows:
        return

    num_cols = max(len(r) for r in rows)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = page_width / num_cols
    line_h = 5

    def draw_row(cells, bold: bool):
        cells = cells + [""] * (num_cols - len(cells))
        pdf.set_font("Helvetica", "B" if bold else "", 8.5)
        wrapped = []
        for c in cells:
            text = _pdf_safe(_strip_md_inline(c))
            lines = pdf.multi_cell(col_width, line_h, text, dry_run=True, output="LINES")
            wrapped.append(lines if lines else [""])
        max_lines = max(len(w) for w in wrapped)

        # Page-break check: if this row won't fit, start a fresh page
        # first, so a single row never gets split awkwardly across pages.
        if pdf.get_y() + max_lines * line_h > pdf.page_break_trigger:
            pdf.add_page()

        x0, y0 = pdf.get_x(), pdf.get_y()
        for i, lines in enumerate(wrapped):
            padded = lines + [""] * (max_lines - len(lines))
            pdf.set_xy(x0 + i * col_width, y0)
            pdf.multi_cell(col_width, line_h, "\n".join(padded), border=1)
        pdf.set_xy(x0, y0 + max_lines * line_h)

    draw_row(rows[0], bold=True)
    for row in rows[1:]:
        draw_row(row, bold=False)
    pdf.ln(3)


def _fix_runon_contact_line(text: str) -> str:
    """
    Safety net for cover letters: even with explicit prompt instructions,
    a model can occasionally still cram name/location/phone/email/links
    onto one dash-separated line. If a line contains an email address AND
    3+ " - " separators, it's almost certainly a mis-formatted contact
    block -- split it onto separate lines rather than showing it as one
    unreadable run-on sentence.
    """
    lines = text.split("\n")
    fixed = []
    for line in lines:
        has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", line))
        dash_count = line.count(" - ")
        if has_email and dash_count >= 2:
            parts = [p.strip() for p in line.split(" - ") if p.strip()]
            fixed.extend(parts)
        else:
            fixed.append(line)
    return "\n".join(fixed)


def _render_markdown_text(pdf: FPDF, text: str):
    """
    Renders markdown as an actually-formatted PDF section instead of
    dumping raw '**bold**' / '# heading' / '| table |' syntax onto the
    page. Handles headers, bold-only lines, horizontal rules, pipe
    tables, plain paragraphs, and a one-time "letterhead" treatment for
    cover letters: the first bold line (the applicant's name) is sized
    up, and a contact-info line immediately after it (email/links/
    pipe-separated) is styled smaller and muted instead of both just
    blending into the body text at equal weight.
    """
    text = _fix_runon_contact_line(text)
    lines = text.split("\n")
    i = 0
    is_first_content_line = True
    prev_was_name_line = False

    while i < len(lines):
        raw_line = lines[i]
        stripped = raw_line.strip()

        if not stripped:
            pdf.ln(2)
            i += 1
            continue  # blank line doesn't cancel a pending "name -> contact" pairing

        was_first_line = is_first_content_line
        is_first_content_line = False

        # Horizontal rule: a line of only dashes
        if len(stripped) >= 3 and set(stripped) <= {"-"}:
            prev_was_name_line = False
            y = pdf.get_y()
            pdf.set_draw_color(210, 210, 210)
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)
            i += 1
            continue

        # Markdown table block -- consume all consecutive "| ... |" lines
        if stripped.startswith("|"):
            prev_was_name_line = False
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            _render_md_table(pdf, table_lines)
            continue

        # Headers: #, ##, ###
        heading_match = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if heading_match:
            prev_was_name_line = False
            level = len(heading_match.group(1))
            heading_text = _strip_md_inline(heading_match.group(2))
            size = {1: 15, 2: 13, 3: 12}.get(level, 11)
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", size)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 7, _pdf_safe(heading_text), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            i += 1
            continue

        # Bullet list item
        bullet_match = re.match(r"^[-*\u2022]\s+(.*)", stripped)
        if bullet_match:
            prev_was_name_line = False
            item_text = _strip_md_inline(bullet_match.group(1))
            pdf.set_font("Helvetica", "", 10.5)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 6, _pdf_safe("-  " + item_text), new_x="LMARGIN", new_y="NEXT")
            i += 1
            continue

        # Blockquote line
        quote_match = re.match(r"^>\s?(.*)", stripped)
        if quote_match:
            prev_was_name_line = False
            quote_text = _strip_md_inline(quote_match.group(1))
            pdf.set_font("Helvetica", "I", 10.5)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 6, _pdf_safe("    " + quote_text), new_x="LMARGIN", new_y="NEXT")
            i += 1
            continue

        is_whole_bold = bool(re.match(r"^\*\*(.+)\*\*$", stripped))
        clean_text = _strip_md_inline(stripped)

        # First content line of the whole document, short enough to be a
        # name (not a full sentence) -> treat as a letterhead name. Covers
        # both "**Aryan Gupta**" and a plain unmarked "Aryan Gupta".
        if was_first_line and len(clean_text) <= 60:
            prev_was_name_line = True
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 8, _pdf_safe(clean_text), new_x="LMARGIN", new_y="NEXT")
            i += 1
            continue

        # Line right after the name that looks like contact info
        looks_like_contact = bool(
            re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", stripped)
            or "linkedin.com" in stripped.lower()
            or "github.com" in stripped.lower()
            or stripped.count(" | ") >= 1
        )
        if prev_was_name_line and looks_like_contact:
            prev_was_name_line = False
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(110, 110, 110)
            pdf.multi_cell(0, 5, _pdf_safe(clean_text), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            i += 1
            continue

        prev_was_name_line = False
        pdf.set_font("Helvetica", "B" if is_whole_bold else "", 10.5)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 6, _pdf_safe(clean_text), new_x="LMARGIN", new_y="NEXT")
        i += 1


def _pdf_write_value(pdf: FPDF, value, indent: int = 0):
    pad = "    " * indent
    if isinstance(value, dict):
        for k, v in value.items():
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _pdf_safe(pad + k.replace("_", " ").title() + ":"), new_x="LMARGIN", new_y="NEXT")
            _pdf_write_value(pdf, v, indent + 1)
    elif isinstance(value, list):
        pdf.set_font("Helvetica", "", 11)
        for item in value:
            pdf.multi_cell(0, 6, _pdf_safe(pad + "- " + _strip_md_inline(str(item))), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _pdf_safe(pad + _strip_md_inline(str(value))), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def build_pdf_report(analysis_type: str, model_used: str, data) -> bytes:
    """
    Builds a branded PDF from an analysis result. `data` is either the
    dict returned for ats_score/keyword_gap modes, or the plain markdown
    string returned for detailed/cover_letter modes.

    Uses multi_cell exclusively (never cell(w=0, ...)) -- fpdf2's
    zero-width cell() combined with the deprecated ln=True does not
    reliably reset the cursor to the left margin, which causes
    "not enough horizontal space" crashes on the line after. multi_cell
    always resets correctly, so we use it even for single-line text.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(0, 12, _pdf_safe("ATSight"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 8, _pdf_safe(analysis_type.replace("_", " ").title() + " Report"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(0, 6, _pdf_safe(f"Model: {model_used}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_draw_color(210, 210, 210)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(6)

    pdf.set_text_color(20, 20, 20)
    if analysis_type == "cover_letter" and isinstance(data, dict):
        _render_cover_letter_pdf(pdf, data)
    elif isinstance(data, dict):
        _pdf_write_value(pdf, data)
    else:
        _render_markdown_text(pdf, str(data))

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, _pdf_safe("Generated by ATSight. AI analysis is for guidance only -- always verify with human review."), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def _render_cover_letter_pdf(pdf: FPDF, data: dict):
    """
    Deterministic cover-letter layout built from structured fields
    (candidate_name, location, phone, email, linkedin, github,
    salutation, body_paragraphs, closing) instead of trusting the
    model's own prose formatting for the header -- that's what caused
    inconsistent, unprofessional-looking contact lines run to run.
    """
    name = _pdf_safe(data.get("candidate_name", ""))
    contact_parts = [p for p in [
        data.get("location", ""), data.get("phone", ""), data.get("email", ""),
    ] if p]
    link_parts = [p for p in [data.get("linkedin", ""), data.get("github", "")] if p]

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, name, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(100, 100, 100)
    if contact_parts:
        pdf.multi_cell(0, 5.5, _pdf_safe("  |  ".join(contact_parts)), new_x="LMARGIN", new_y="NEXT")
    if link_parts:
        pdf.multi_cell(0, 5.5, _pdf_safe("  |  ".join(link_parts)), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 6, _pdf_safe(data.get("salutation", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for para in data.get("body_paragraphs", []):
        pdf.multi_cell(0, 6, _pdf_safe(_strip_md_inline(str(para))), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.multi_cell(0, 6, _pdf_safe(data.get("closing", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 6, name, new_x="LMARGIN", new_y="NEXT")


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