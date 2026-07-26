# ATSight

**AI-powered resume intelligence — see exactly how your resume reads to an applicant tracking system before a recruiter ever does.**

🔗 **Live app:** [atsight.streamlit.app](https://atsight.streamlit.app/)

---

## What it does

ATSight analyzes your resume against a job description and gives you an ATS-grade read on where you stand — powered by Groq's LLM API, with your history saved securely per account via Supabase.

**Four analysis modes:**
- **ATS Score** — overall compatibility score, category breakdown (keyword/experience/skills/education/formatting/readability), pass/fail prediction, matched vs. missing keywords
- **Keyword Gap** — focused matched/missing keyword comparison with suggestions
- **Detailed Report** — full narrative analysis: strengths, gaps, actionable recommendations
- **Cover Letter** — AI-drafted, tailored to the specific job description

Every result can be downloaded as a clean, formatted **PDF**.

---

## Screenshots

**Login**
![Login page](Screenshots/Login%20page.png)

**Home**
![Home page](Screenshots/Home%20page.png)

**Upload**
![Upload page](Screenshots/Upload%20page.png)

**Analysis Dashboard**
![Analysis Dashboard](Screenshots/Analysis%20Dashboard.png)

**Detailed Report**
![Detailed Report](Screenshots/Detailed%20Report.png)

**Cover Letter**
![Cover Letter](Screenshots/Cover%20Letter.png)

---

## Key features

- 🔐 **Account-based** — register/log in, your analyses are private to you (Supabase Auth + Row Level Security)
- 📊 **Persistent history** — every analysis is saved; revisit past runs anytime from the History tab
- ⚡ **Async AI calls** — non-blocking Groq API integration (`AsyncGroq`), with automatic fallback handling if a model returns malformed output
- 🧠 **Multiple models** — pick between GPT-OSS 20B (fast), GPT-OSS 120B (most accurate), or Qwen 3.6 27B (balanced)
- 📄 **Robust PDF parsing** — cascading extraction (pdfplumber → PyPDF2 → PyMuPDF) so more resume formats actually work
- 🛡️ **Admin dashboard** — for admin accounts only: total users, total analyses, API usage, recent signups
- 🎨 **Editorial dark UI** — a custom design system, not default Streamlit styling
- 📥 **PDF export** — properly formatted downloadable reports and cover letters, not raw text dumps

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend / App | Streamlit |
| Auth & Database | Supabase (PostgreSQL + Auth, Row Level Security) |
| AI | Groq API (`AsyncGroq`) — GPT-OSS 20B/120B, Qwen 3.6 27B |
| PDF parsing | pdfplumber, PyPDF2, PyMuPDF |
| PDF generation | fpdf2 |
| Charts | Plotly |
| Data | Pandas |

---

## Project structure

```
ATSight/
├── app.py            # Main entry point, navigation, page wiring
├── auth.py           # Supabase Auth: login / register / logout / session state
├── database.py       # History persistence + admin aggregate metrics
├── analyzer.py        # Async Groq calls, PDF extraction, JSON schema validation
├── styles.py           # Design system (CSS), chart theming, PDF report builder
├── requirements.txt
├── runtime.txt
├── .streamlit/
│   ├── config.toml     # Theme + toolbar config
│   └── secrets.toml     # API keys (gitignored, not committed)
└── .gitignore
```

---

## Running it locally

### 1. Clone and install
```bash
git clone https://github.com/aryan16-git/ATSight.git
cd ATSight
pip install -r requirements.txt
```

### 2. Set up Supabase
- Create a free project at [supabase.com](https://supabase.com)
- Run the schema (tables: `profiles`, `analyses`, `api_usage` with Row Level Security) in the SQL Editor
- Grab your **Project URL**, **anon key**, and **service_role key** from Settings → API

### 3. Get a Groq API key
Free at [console.groq.com](https://console.groq.com)

### 4. Configure secrets
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
SUPABASE_SERVICE_KEY = "eyJ..."
```

### 5. Run
```bash
streamlit run app.py
```

---

## Deployment

Deployed on **Streamlit Community Cloud**, auto-redeploying from the `main` branch. Secrets are configured separately in the Streamlit Cloud dashboard (Settings → Secrets) — never committed to the repo.

---

## Disclaimer

AI analysis is for guidance only — always verify recommendations with human judgment before making resume decisions.

---

## Author

**Aryan Gupta**
[GitHub](https://github.com/aryan16-git) · [LinkedIn](https://linkedin.com/in/aryan-gupta-d16m08)