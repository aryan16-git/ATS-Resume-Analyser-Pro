"""
app.py
ATS Resume Analyser PRO -- main entry point.

Flow:
1. Configure page + inject design system.
2. Gate on auth -- logged-out users only ever see render_auth_page().
3. Sidebar: user info, logout, model picker.
4. Tabs: Upload -> Analyze -> Dashboard -> History (+ Admin, if is_admin).
"""

from datetime import datetime

import streamlit as st

from auth import (
    init_auth_session_state,
    is_logged_in,
    render_auth_page,
    render_logout_button,
    get_current_user,
    get_current_user_id,
)
from database import (
    save_analysis,
    get_user_history,
    log_api_usage,
    admin_get_summary_metrics,
    admin_get_recent_users,
    admin_get_analysis_type_breakdown,
)
from analyzer import (
    AVAILABLE_MODELS,
    extract_text_from_pdf,
    get_file_stats,
    run_analysis,
)
from styles import (
    inject_custom_css,
    render_masthead,
    render_stat_card,
    render_skeleton_loader,
    create_gauge_chart,
    create_radar_chart,
)


# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="ATS Resume Analyser PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()
init_auth_session_state()


# ============ AUTH GATE ============
if not is_logged_in():
    render_masthead(
        eyebrow="AI-Powered Resume Intelligence",
        title="ATS Resume Analyser",
        subtitle="See exactly how your resume reads to an applicant tracking system before a recruiter ever does.",
    )
    render_auth_page()
    st.stop()  # nothing below this line renders for logged-out users


# ============ SESSION STATE (analysis-specific) ============
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""
if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""
if "current_result" not in st.session_state:
    st.session_state.current_result = None  # dict from analyzer.run_analysis
if "current_analysis_type" not in st.session_state:
    st.session_state.current_analysis_type = None
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True


# ============ CUSTOM SIDEBAR TOGGLE ============
# Streamlit's own built-in collapse arrow proved unreliable to restyle
# reliably (its internal test-ids/behavior shift between versions), so
# instead of fighting it we hide it and drive visibility ourselves with
# one button we fully control.
st.markdown("""
<style>
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

toggle_label = "✕ Hide menu" if st.session_state.sidebar_open else "☰ Menu"
if st.button(toggle_label, key="custom_sidebar_toggle"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()

if not st.session_state.sidebar_open:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### Control Panel")
    render_logout_button(location="sidebar")

    if st.session_state.get("is_admin"):
        st.markdown("🛡️ **Admin access enabled**")

    st.markdown("---")
    st.markdown("**AI Model**")
    selected_model_label = st.selectbox(
        "Choose model:",
        list(AVAILABLE_MODELS.keys()),
        label_visibility="collapsed",
    )
    model_id = AVAILABLE_MODELS[selected_model_label]

    st.markdown("---")
    if st.button("Clear current session", use_container_width=True):
        st.session_state.resume_text = ""
        st.session_state.resume_filename = ""
        st.session_state.job_desc = ""
        st.session_state.current_result = None
        st.session_state.current_analysis_type = None
        st.rerun()


# ============ MASTHEAD ============
render_masthead(
    eyebrow="AI-Powered Resume Intelligence",
    title="ATS Resume Analyser",
    subtitle="Upload your resume, paste a job description, and get an ATS-grade read on where you stand.",
)

user = get_current_user()
user_id = get_current_user_id()

tab_labels = ["Upload", "Analyze", "Dashboard", "History"]
if st.session_state.get("is_admin"):
    tab_labels.append("Admin")

tabs = st.tabs(tab_labels)
tab_upload, tab_analyze, tab_dashboard, tab_history = tabs[:4]
tab_admin = tabs[4] if len(tabs) == 5 else None


# ============ TAB: UPLOAD ============
with tab_upload:
    col_main, col_help = st.columns([2, 1])

    with col_main:
        st.markdown("### Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF):", type=["pdf"], label_visibility="collapsed"
        )

        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            stats = get_file_stats(file_bytes, uploaded_file.name)

            c1, c2, c3 = st.columns(3)
            with c1:
                render_stat_card("File", stats["filename"][:20])
            with c2:
                render_stat_card("Size", f"{stats['size_mb']} MB")
            with c3:
                render_stat_card("Pages", str(stats["pages"] or "N/A"))

            with st.spinner("Extracting text..."):
                extracted = extract_text_from_pdf(file_bytes, uploaded_file.name)

            if not extracted:
                st.error(
                    "Could not extract text from this PDF. Make sure it's a "
                    "text-based PDF (not a scanned image) and isn't password-protected."
                )
            else:
                st.session_state.resume_text = extracted
                st.session_state.resume_filename = uploaded_file.name
                with st.expander("Preview extracted text"):
                    st.text_area(
                        "extracted_preview",
                        extracted[:1500] + ("..." if len(extracted) > 1500 else ""),
                        height=250,
                        label_visibility="collapsed",
                    )

        st.markdown("### Job Description")
        job_desc = st.text_area(
            "Paste the job description:",
            height=220,
            value=st.session_state.job_desc,
            placeholder="Paste the full job posting here -- include requirements and responsibilities for best results.",
            label_visibility="collapsed",
        )
        st.session_state.job_desc = job_desc
        if job_desc:
            st.caption(f"{len(job_desc.split())} words")

    with col_help:
        st.markdown("### Ready Check")
        render_stat_card(
            "Resume", "✓" if st.session_state.resume_text else "—",
            "Uploaded" if st.session_state.resume_text else "Required",
            tone="success" if st.session_state.resume_text else "default",
        )
        st.write("")
        render_stat_card(
            "Job Description", "✓" if st.session_state.job_desc else "—",
            "Added" if st.session_state.job_desc else "Required",
            tone="success" if st.session_state.job_desc else "default",
        )
        st.write("")
        st.info(
            "Once both are ready, head to the **Analyze** tab and pick "
            "a mode: ATS Score, Keyword Gap, Detailed Report, or Cover Letter."
        )


# ============ TAB: ANALYZE ============
with tab_analyze:
    ready = bool(st.session_state.resume_text) and bool(st.session_state.job_desc)

    if not ready:
        st.warning("Upload a resume and paste a job description in the **Upload** tab first.")
    else:
        st.markdown("### Choose Analysis Type")
        c1, c2, c3, c4 = st.columns(4)
        mode_clicked = None
        with c1:
            if st.button("ATS Score", use_container_width=True):
                mode_clicked = "ats_score"
        with c2:
            if st.button("Keyword Gap", use_container_width=True):
                mode_clicked = "keyword_gap"
        with c3:
            if st.button("Detailed Report", use_container_width=True):
                mode_clicked = "detailed"
        with c4:
            if st.button("Cover Letter", use_container_width=True):
                mode_clicked = "cover_letter"

        result_area = st.empty()

        if mode_clicked:
            with result_area.container():
                st.markdown(f"Running **{mode_clicked.replace('_', ' ').title()}** with {selected_model_label}...")
                render_skeleton_loader()

            result = run_analysis(
                model_id, mode_clicked,
                st.session_state.job_desc, st.session_state.resume_text,
            )

            log_api_usage(
                user_id=user_id,
                endpoint=mode_clicked,
                tokens_used=result.get("tokens_used", 0),
                latency_ms=result.get("latency_ms", 0),
                success=result.get("success", False),
            )

            if result["success"]:
                st.session_state.current_result = result
                st.session_state.current_analysis_type = mode_clicked

                overall_score = None
                if isinstance(result["data"], dict):
                    overall_score = result["data"].get("overall_score")

                ok, msg = save_analysis(
                    user_id=user_id,
                    analysis_type=mode_clicked,
                    model_used=model_id,
                    job_description=st.session_state.job_desc,
                    resume_filename=st.session_state.resume_filename,
                    result_json=result["data"] if isinstance(result["data"], dict) else {"text": result["data"]},
                    overall_score=overall_score,
                )
                if ok:
                    get_user_history.clear()
                else:
                    st.warning(f"Analysis succeeded but couldn't be saved to history: {msg}")

                result_area.empty()
            else:
                result_area.empty()
                st.error(result["error"])
                if "raw_fallback" in result:
                    with st.expander("Show raw model output"):
                        st.code(result["raw_fallback"])

        # ---- Render whatever the current result is (from this run or a loaded one) ----
        if st.session_state.current_result and st.session_state.current_result.get("success"):
            data = st.session_state.current_result["data"]
            a_type = st.session_state.current_analysis_type

            st.markdown("---")
            st.markdown(f"### Results — {a_type.replace('_', ' ').title()}")

            if a_type == "ats_score" and isinstance(data, dict):
                col_gauge, col_meta = st.columns([2, 1])
                with col_gauge:
                    st.plotly_chart(
                        create_gauge_chart(data.get("overall_score", 0), "Overall ATS Score"),
                        use_container_width=False,
                    )
                with col_meta:
                    pred = data.get("prediction", {})
                    render_stat_card(
                        "ATS Status", "PASS" if pred.get("pass_ats") else "FAIL",
                        pred.get("interview_probability", ""),
                        tone="success" if pred.get("pass_ats") else "danger",
                    )
                    st.write("")
                    render_stat_card("Shortlist Time", pred.get("shortlist_time", "N/A"))

                breakdown = data.get("breakdown", {})
                if breakdown:
                    st.plotly_chart(
                        create_radar_chart(breakdown, "Score Breakdown"),
                        use_container_width=True,
                    )

                kw = data.get("keywords", {})
                col_m, col_x = st.columns(2)
                with col_m:
                    st.markdown("**Matching Keywords**")
                    for k in kw.get("matched", []):
                        st.markdown(f"- {k}")
                with col_x:
                    st.markdown("**Missing Keywords**")
                    for k in kw.get("missing", []):
                        st.markdown(f"- {k}")

                improvements = data.get("improvements", [])
                if improvements:
                    st.markdown("**Improvement Suggestions**")
                    for i, imp in enumerate(improvements, 1):
                        st.markdown(f"{i}. {imp}")

            elif a_type == "keyword_gap" and isinstance(data, dict):
                col_m, col_x = st.columns(2)
                with col_m:
                    st.markdown("**Matched Keywords**")
                    for k in data.get("matched_keywords", []):
                        st.markdown(f"- {k}")
                with col_x:
                    st.markdown("**Missing Keywords**")
                    for k in data.get("missing_keywords", []):
                        st.markdown(f"- {k}")
                suggestions = data.get("suggestions", [])
                if suggestions:
                    st.markdown("**Suggestions**")
                    for s in suggestions:
                        st.markdown(f"- {s}")

            else:  # detailed / cover_letter -- plain markdown text
                st.markdown(data)

            st.download_button(
                "Download this result",
                data=data if isinstance(data, str) else str(data),
                file_name=f"ats_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )


# ============ TAB: DASHBOARD ============
with tab_dashboard:
    if not (
        st.session_state.current_result
        and st.session_state.current_result.get("success")
        and st.session_state.current_analysis_type == "ats_score"
    ):
        st.info("Run an **ATS Score** analysis first to see the dashboard.")
    else:
        data = st.session_state.current_result["data"]
        score = data.get("overall_score", 0)
        pred = data.get("prediction", {})

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_stat_card("Overall Score", f"{score}%", "ATS Compatibility", tone="accent")
        with c2:
            render_stat_card(
                "ATS Status", "PASS" if pred.get("pass_ats") else "FAIL",
                "Screening Result", tone="success" if pred.get("pass_ats") else "danger",
            )
        with c3:
            render_stat_card("Interview Chance", pred.get("interview_probability", "N/A"), "Probability")
        with c4:
            render_stat_card("Shortlist Time", pred.get("shortlist_time", "N/A"), "Estimate")

        st.markdown("---")
        col_g, col_r = st.columns(2)
        with col_g:
            st.plotly_chart(create_gauge_chart(score, "Overall ATS Score"), use_container_width=False)
        with col_r:
            breakdown = data.get("breakdown", {})
            if breakdown:
                st.plotly_chart(create_radar_chart(breakdown, "Skills Breakdown"), use_container_width=True)


# ============ TAB: HISTORY ============
with tab_history:
    st.markdown("### Your Analysis History")
    history = get_user_history(user_id)

    if not history:
        st.info("No analyses yet. Run one from the **Analyze** tab and it'll show up here.")
    else:
        for row in history:
            created = row.get("created_at", "")[:19].replace("T", " ")
            label = f"{row.get('analysis_type', '').replace('_', ' ').title()} — {created}"
            with st.expander(label):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**File:** {row.get('resume_filename', 'N/A')}")
                    st.write(f"**Model:** {row.get('model_used', 'N/A')}")
                with col_b:
                    if row.get("overall_score") is not None:
                        render_stat_card("Score", f"{row['overall_score']}%")

                if st.button("Load into Analyze tab", key=f"load_{row['id']}"):
                    st.session_state.current_result = {"success": True, "data": row["result_json"]}
                    st.session_state.current_analysis_type = row["analysis_type"]
                    st.rerun()


# ============ TAB: ADMIN ============
if tab_admin is not None:
    with tab_admin:
        st.markdown("### Admin Dashboard")
        metrics = admin_get_summary_metrics()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_stat_card("Total Users", str(metrics["total_users"]), tone="accent")
        with c2:
            render_stat_card("Total Analyses", str(metrics["total_analyses"]))
        with c3:
            render_stat_card("Total API Calls", str(metrics["total_api_calls"]))
        with c4:
            render_stat_card("Logins (7d)", str(metrics["recent_logins_7d"]))

        st.markdown("---")
        st.markdown("#### Analysis Type Breakdown")
        breakdown = admin_get_analysis_type_breakdown()
        if breakdown:
            cols = st.columns(len(breakdown))
            for col, (k, v) in zip(cols, breakdown.items()):
                with col:
                    render_stat_card(k.replace("_", " ").title(), str(v))
        else:
            st.info("No analyses recorded yet.")

        st.markdown("---")
        st.markdown("#### Recent Users")
        recent_users = admin_get_recent_users()
        for u in recent_users:
            admin_badge = " 🛡️" if u.get("is_admin") else ""
            st.markdown(
                f"- **{u.get('full_name', 'N/A')}**{admin_badge} — {u.get('email')} "
                f"— joined {str(u.get('created_at', ''))[:10]}"
            )


# ============ FOOTER ============
st.markdown("---")
st.caption(
    "ATS Resume Analyser PRO · AI analysis is for guidance only — always verify with human review."
)