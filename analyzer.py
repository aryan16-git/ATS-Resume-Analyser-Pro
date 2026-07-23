"""
analyzer.py
The AI + PDF engine for ATS Resume Analyser PRO.

- PDF extraction is cached with @st.cache_data so re-running an
  analysis on the same uploaded file doesn't re-parse the PDF.
- Groq calls go through AsyncGroq so the UI thread isn't blocked;
  app.py calls the sync wrapper `run_analysis()`, which internally
  drives the async client with asyncio.run().
- "ats_score" and "keyword_gap" modes demand strict JSON back from the
  model. We ask for it via response_format=json_object AND validate the
  shape ourselves -- if either the API call or the JSON shape fails, we
  return a structured error dict instead of raising, so app.py can
  render a clean fallback UI instead of crashing.
"""

import asyncio
import io
import json
import time
from typing import Optional

import streamlit as st
from groq import AsyncGroq

import pdfplumber
import PyPDF2
import fitz  # PyMuPDF


# ============ MODELS ============

AVAILABLE_MODELS = {
    "⚡ GPT-OSS 20B (Fast & Free)": "openai/gpt-oss-20b",
    "🧠 GPT-OSS 120B (Most Accurate)": "openai/gpt-oss-120b",
    "💎 Qwen 3.6 27B (Balanced)": "qwen/qwen3.6-27b",
}
# Note: llama-3.1-8b-instant, llama-3.3-70b-versatile, and gemma2-9b-it are
# all deprecated on Groq (gemma2-9b-it shut down Oct 2025; the two llama
# models are scheduled for shutdown 08/16/2026). Check
# https://console.groq.com/docs/deprecations before reusing old model IDs.

# Modes that require the model to return strict JSON we then validate.
JSON_MODES = {"ats_score", "keyword_gap"}

# The minimal shape we require for each JSON mode. Used only to check
# the top-level keys are present -- not a full schema validator, but
# enough to catch a malformed or truncated response before it hits the UI.
REQUIRED_KEYS = {
    "ats_score": {"overall_score", "breakdown", "prediction", "keywords", "improvements"},
    "keyword_gap": {"matched_keywords", "missing_keywords", "suggestions"},
}


# ============ CLIENT ============

def get_async_groq_client() -> AsyncGroq:
    """Fresh AsyncGroq client using the key from Streamlit Secrets."""
    api_key = st.secrets["GROQ_API_KEY"]
    return AsyncGroq(api_key=api_key)


# ============ PDF EXTRACTION (cached) ============

@st.cache_data(show_spinner=False)
def extract_text_from_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from PDF bytes, trying multiple libraries in order of
    reliability. Cached on (file_bytes, filename) -- re-uploading the
    exact same file returns instantly instead of re-parsing.
    """
    text = ""

    # Method 1: pdfplumber (best general-purpose extraction)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if len(text.strip()) > 100:
            return text[:6000]
    except Exception:
        pass

    # Method 2: PyPDF2
    try:
        text = ""
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        if len(text.strip()) > 100:
            return text[:6000]
    except Exception:
        pass

    # Method 3: PyMuPDF (fitz) -- last resort, handles some odd encodings
    try:
        text = ""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
        if len(text.strip()) > 50:
            return text[:6000]
    except Exception:
        pass

    return ""  # app.py checks for empty string and shows a clear error


@st.cache_data(show_spinner=False)
def get_file_stats(file_bytes: bytes, filename: str) -> dict:
    """Basic file metadata + page count."""
    stats = {
        "filename": filename,
        "size_mb": round(len(file_bytes) / (1024 * 1024), 2),
        "pages": 0,
    }
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            stats["pages"] = len(pdf.pages)
    except Exception:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            stats["pages"] = len(doc)
            doc.close()
        except Exception:
            pass
    return stats


# ============ PROMPTS ============

def _build_prompt(analysis_type: str, job_desc: str, resume_text: str) -> dict:
    job_desc = job_desc[:2500]
    resume_text = resume_text[:2500]

    if analysis_type == "detailed":
        return {
            "system": (
                "You are an expert HR Director with 20+ years in tech recruitment. "
                "Give detailed, specific, actionable feedback grounded in the actual "
                "resume and job description text provided. Do not invent details."
            ),
            "user": f"""Write a comprehensive resume analysis report in Markdown with these sections:
1. Executive Summary (overall match %, one-line verdict)
2. Quantitative Assessment (skills/experience alignment scores out of 10)
3. Strengths Identified (5-7 specific points citing the resume)
4. Areas for Improvement (5-7 specific, actionable points)
5. Keyword Analysis (top matching and missing keywords)
6. ATS Optimization Score breakdown
7. Hiring Probability Prediction
8. Top 5 Actionable Recommendations

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}""",
        }

    if analysis_type == "ats_score":
        return {
            "system": (
                "You are an ATS algorithm. Respond with ONLY valid JSON, no prose, "
                "no markdown fences, matching the exact schema requested."
            ),
            "user": f"""Analyze this resume against the job description and return ONLY this JSON structure:
{{
  "overall_score": <0-100 integer>,
  "breakdown": {{
    "keyword_match": <0-100>, "experience_match": <0-100>, "skills_match": <0-100>,
    "education_match": <0-100>, "formatting": <0-100>, "readability": <0-100>
  }},
  "prediction": {{
    "pass_ats": <true/false>, "interview_probability": "High/Medium/Low",
    "shortlist_time": "Immediate/1-3 days/1 week+"
  }},
  "keywords": {{
    "matched": [<up to 8 strings>], "missing": [<up to 8 strings>]
  }},
  "improvements": [<3-5 short actionable strings>]
}}

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}""",
        }

    if analysis_type == "keyword_gap":
        return {
            "system": (
                "You are a keyword-matching engine for resumes. Respond with ONLY "
                "valid JSON, no prose, no markdown fences."
            ),
            "user": f"""Compare the resume to the job description and return ONLY this JSON structure:
{{
  "matched_keywords": [<strings found in both>],
  "missing_keywords": [<important JD terms absent from resume>],
  "suggestions": [<3-5 short strings on how to naturally add the missing keywords>]
}}

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}""",
        }

    if analysis_type == "cover_letter":
        return {
            "system": (
                "You are a professional cover letter writer specializing in tech "
                "roles. Write confident, specific, non-generic cover letters."
            ),
            "user": f"""Write a 250-350 word professional cover letter tailored to this job,
using specific details from the resume. Include a header, salutation, 3 body
paragraphs, and a professional close.

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}""",
        }

    raise ValueError("Unknown analysis_type: " + analysis_type)


# ============ CORE ASYNC CALL ============

async def _call_groq_async(
    model: str, analysis_type: str, job_desc: str, resume_text: str
) -> dict:
    """
    Makes the actual AsyncGroq call. Returns a result dict that always
    has a 'success' key, so callers never need a try/except of their own.
    """
    client = get_async_groq_client()
    prompt = _build_prompt(analysis_type, job_desc, resume_text)
    start = time.monotonic()

    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        temperature=0.6,
        max_tokens=3000,
    )
    if analysis_type in JSON_MODES:
        kwargs["response_format"] = {"type": "json_object"}
        # GPT-OSS 20B/120B and Qwen 3.6 27B are reasoning models -- without
        # this they can spend the whole max_tokens budget "thinking" and
        # leave nothing for the actual JSON, causing an empty/truncated
        # response that fails Groq's json_validate check. We don't need
        # chain-of-thought for structured extraction, so keep it minimal.
        # NOTE: accepted values differ by model family -- GPT-OSS models
        # take "low"/"medium"/"high", Qwen 3.6 27B only takes
        # "none"/"default". Pick the right one per model.
        if model.startswith("qwen/"):
            kwargs["reasoning_effort"] = "none"
        else:
            kwargs["reasoning_effort"] = "low"

    try:
        response = await client.chat.completions.create(**kwargs)
    except Exception as e:
        return {
            "success": False,
            "error": "Groq API call failed: " + str(e),
            "latency_ms": int((time.monotonic() - start) * 1000),
            "tokens_used": 0,
        }

    latency_ms = int((time.monotonic() - start) * 1000)
    raw_content = response.choices[0].message.content
    tokens_used = getattr(response.usage, "total_tokens", 0) if response.usage else 0

    if analysis_type not in JSON_MODES:
        return {
            "success": True,
            "data": raw_content,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
        }

    # ---- Strict JSON validation with a fallback path ----
    parsed, parse_error = _parse_and_validate_json(raw_content, analysis_type)
    if parsed is not None:
        return {
            "success": True,
            "data": parsed,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
        }

    return {
        "success": False,
        "error": "Model returned malformed JSON (" + str(parse_error) + ").",
        "raw_fallback": raw_content,  # app.py can still show something useful
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
    }


def _parse_and_validate_json(raw: str, analysis_type: str):
    """Returns (parsed_dict_or_None, error_message_or_None)."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, "invalid JSON: " + str(e)

    required = REQUIRED_KEYS.get(analysis_type, set())
    missing = required - parsed.keys()
    if missing:
        return None, "missing keys: " + str(sorted(missing))

    return parsed, None


# ============ SYNC WRAPPER (what app.py calls) ============

def run_analysis(
    model: str, analysis_type: str, job_desc: str, resume_text: str
) -> dict:
    """
    Synchronous entry point for Streamlit. Internally drives the async
    Groq call. Always returns a dict with a 'success' bool -- app.py
    should branch on that rather than expecting exceptions.
    """
    return asyncio.run(
        _call_groq_async(model, analysis_type, job_desc, resume_text)
    )