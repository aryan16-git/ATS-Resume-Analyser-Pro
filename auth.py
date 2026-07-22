"""
auth.py
Authentication & session management for ATS Resume Analyser PRO.
Wraps Supabase Auth (email + password) and exposes simple helpers
that app.py can call without knowing anything about Supabase.
"""

import streamlit as st
from supabase import create_client, Client


# ============ CLIENT SETUP ============

@st.cache_resource
def get_supabase_client() -> Client:
    """
    Create a cached Supabase client using the anon key.
    Cached so we don't reconnect on every Streamlit rerun.
    """
    url = st.secrets["SUPABASE_URL"]
    anon_key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, anon_key)


@st.cache_resource
def get_supabase_admin_client() -> Client:
    """
    Separate client using the service_role key.
    ONLY use this for admin-only queries (e.g. Admin Dashboard metrics
    across all users). Never expose this client or its results to
    non-admin users.
    """
    url = st.secrets["SUPABASE_URL"]
    service_key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, service_key)


# ============ SESSION STATE HELPERS ============

def init_auth_session_state():
    """Call once near the top of app.py, before anything else."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def get_current_user():
    """Returns the Supabase user object (or None)."""
    return st.session_state.get("user")


def get_current_user_id():
    user = get_current_user()
    return user.id if user else None


# ============ CORE AUTH ACTIONS ============

def sign_up(email: str, password: str, full_name: str) -> tuple[bool, str]:
    """
    Register a new user. Returns (success, message).
    A `profiles` row is auto-created by the DB trigger from schema.sql.
    """
    client = get_supabase_client()
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}},
        })
        if response.user is None:
            return False, "Sign up failed. Please try again."
        return True, "Account created! You can now log in."
    except Exception as e:
        return False, f"Sign up failed: {str(e)}"


def sign_in(email: str, password: str) -> tuple[bool, str]:
    """
    Log in an existing user. On success, populates st.session_state.
    Returns (success, message).
    """
    client = get_supabase_client()
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response.user is None or response.session is None:
            return False, "Invalid email or password."

        st.session_state.user = response.user
        st.session_state.access_token = response.session.access_token

        _load_profile_and_set_admin_flag(response.user.id)
        _update_last_login(response.user.id)

        return True, "Logged in successfully!"
    except Exception as e:
        return False, f"Login failed: {str(e)}"


def sign_out():
    """Clear the Supabase session and local session state."""
    client = get_supabase_client()
    try:
        client.auth.sign_out()
    except Exception:
        pass  # Even if the remote sign-out call fails, clear local state
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.is_admin = False


# ============ INTERNAL HELPERS ============

def _load_profile_and_set_admin_flag(user_id: str):
    """Fetch the profiles row to check is_admin, store in session state."""
    client = get_supabase_client()
    try:
        result = (
            client.table("profiles")
            .select("is_admin")
            .eq("id", user_id)
            .single()
            .execute()
        )
        st.session_state.is_admin = bool(result.data.get("is_admin", False))
    except Exception:
        st.session_state.is_admin = False


def _update_last_login(user_id: str):
    """Best-effort timestamp update; failures here shouldn't block login."""
    client = get_supabase_client()
    try:
        client.table("profiles").update(
            {"last_login_at": "now()"}
        ).eq("id", user_id).execute()
    except Exception:
        pass


# ============ UI: LOGIN / REGISTER FORM ============

def render_auth_page():
    """
    Renders a centered login/register form.
    Call this from app.py when `not is_logged_in()`, and `return` right
    after so the rest of the app never renders for logged-out users.
    """
    st.markdown("## 🔐 Welcome to ATS Resume Analyser PRO")
    st.caption("Sign in to analyse your resume and track your history.")

    tab_login, tab_register = st.tabs(["Log In", "Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Signing you in..."):
                        success, message = sign_in(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    with tab_register:
        with st.form("register_form"):
            full_name = st.text_input("Full Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            password_confirm = st.text_input(
                "Confirm Password", type="password", key="reg_password_confirm"
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if not full_name or not email or not password:
                    st.error("Please fill in all fields.")
                elif password != password_confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating your account..."):
                        success, message = sign_up(email, password, full_name)
                    if success:
                        st.success(message)
                        st.info("Switch to the **Log In** tab to sign in.")
                    else:
                        st.error(message)


def render_logout_button(location="sidebar"):
    """Small reusable logout button. Place in sidebar or header."""
    container = st.sidebar if location == "sidebar" else st
    user = get_current_user()
    if user:
        container.markdown(f"**Signed in as:** {user.email}")
        if container.button("Log Out", use_container_width=True):
            sign_out()
            st.rerun()