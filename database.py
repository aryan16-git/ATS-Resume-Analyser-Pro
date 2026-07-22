"""
database.py
Persistence layer for ATS Resume Analyser PRO.

- User-scoped functions (save_analysis, get_user_history, ...) use the
  regular Supabase client from auth.py. Because that client is the SAME
  instance used to sign the user in, Supabase's Python SDK keeps the
  user's JWT attached to it -- so Row Level Security enforces "users can
  only see their own rows" automatically. We don't need to filter by
  user_id in the query; RLS does it for us. We still pass user_id
  explicitly on inserts/updates because RLS's `with check` policies
  require it to match auth.uid().

- Admin-only functions use the service_role client, which bypasses RLS
  entirely. Only call these after confirming st.session_state.is_admin
  is True in app.py -- this module does not re-check that itself.
"""

from datetime import datetime, timedelta
from typing import Optional

import streamlit as st

from auth import get_supabase_client, get_supabase_admin_client


# ============ USER: SAVE ANALYSIS ============

def save_analysis(
    user_id: str,
    analysis_type: str,
    model_used: str,
    job_description: str,
    resume_filename: str,
    result_json: dict,
    overall_score: Optional[int] = None,
):
    """
    Persist one analysis run. Call this right after a successful
    AI analysis in app.py. Returns (success, message_or_error).
    """
    client = get_supabase_client()
    try:
        payload = {
            "user_id": user_id,
            "analysis_type": analysis_type,
            "model_used": model_used,
            "job_description": job_description[:5000],  # guard against huge blobs
            "resume_filename": resume_filename,
            "overall_score": overall_score,
            "result_json": result_json,
        }
        client.table("analyses").insert(payload).execute()
        return True, "Analysis saved to history."
    except Exception as e:
        return False, "Could not save analysis: " + str(e)


# ============ USER: READ HISTORY ============

@st.cache_data(ttl=30, show_spinner=False)
def get_user_history(user_id: str, limit: int = 50):
    """
    Fetch this user's past analyses, most recent first.
    Cached for 30s so switching tabs doesn't refire a query every rerun;
    call get_user_history.clear() right after save_analysis if you need
    the History tab to reflect a brand-new save immediately.
    """
    client = get_supabase_client()
    try:
        result = (
            client.table("analyses")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        st.error("Could not load history: " + str(e))
        return []


def get_analysis_by_id(analysis_id: str):
    """Fetch a single analysis (used when a user clicks 'Load' in History)."""
    client = get_supabase_client()
    try:
        result = (
            client.table("analyses")
            .select("*")
            .eq("id", analysis_id)
            .single()
            .execute()
        )
        return result.data
    except Exception:
        return None


# ============ USER: API USAGE LOGGING ============

def log_api_usage(
    user_id: str,
    endpoint: str,
    tokens_used: int = 0,
    latency_ms: int = 0,
    success: bool = True,
):
    """
    Best-effort logging -- call after every Groq call (success or failure).
    Never raises; a logging failure should never break the user's analysis.
    """
    client = get_supabase_client()
    try:
        client.table("api_usage").insert({
            "user_id": user_id,
            "endpoint": endpoint,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "success": success,
        }).execute()
    except Exception:
        pass


# ============ ADMIN: AGGREGATE METRICS ============
# All functions below use the service_role client and see ALL users'
# data. Gate access to these behind st.session_state.is_admin in app.py.

@st.cache_data(ttl=60, show_spinner=False)
def admin_get_summary_metrics():
    """
    Returns the headline numbers for the Admin Dashboard:
    total users, analyses run, API calls, and logins in the last 7 days.
    """
    client = get_supabase_admin_client()
    metrics = {
        "total_users": 0,
        "total_analyses": 0,
        "total_api_calls": 0,
        "recent_logins_7d": 0,
    }

    try:
        profiles = client.table("profiles").select("id, last_login_at").execute()
        metrics["total_users"] = len(profiles.data or [])

        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        metrics["recent_logins_7d"] = sum(
            1 for p in (profiles.data or [])
            if p.get("last_login_at") and p["last_login_at"] > cutoff
        )
    except Exception:
        pass

    try:
        analyses = client.table("analyses").select("id", count="exact").execute()
        metrics["total_analyses"] = analyses.count or 0
    except Exception:
        pass

    try:
        usage = client.table("api_usage").select("id", count="exact").execute()
        metrics["total_api_calls"] = usage.count or 0
    except Exception:
        pass

    return metrics


@st.cache_data(ttl=60, show_spinner=False)
def admin_get_recent_users(limit: int = 20):
    """Most recently created accounts -- for an Admin Dashboard table."""
    client = get_supabase_admin_client()
    try:
        result = (
            client.table("profiles")
            .select("email, full_name, created_at, last_login_at, is_admin")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        st.error("Could not load users: " + str(e))
        return []


@st.cache_data(ttl=60, show_spinner=False)
def admin_get_analysis_type_breakdown():
    """Count of analyses per type (detailed/ats_score/cover_letter/keyword_gap)."""
    client = get_supabase_admin_client()
    breakdown = {}
    try:
        result = client.table("analyses").select("analysis_type").execute()
        for row in result.data or []:
            t = row.get("analysis_type", "unknown")
            breakdown[t] = breakdown.get(t, 0) + 1
    except Exception:
        pass
    return breakdown