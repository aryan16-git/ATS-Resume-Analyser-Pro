"""
🚀 ATS Resume Analyzer PRO
Advanced AI-powered resume optimization tool
"""

# ============ IMPORTS ============
import streamlit as st
import os
import tempfile
import json
from datetime import datetime
import base64
import io
import time

# Import Groq AI
from groq import Groq


# Import data visualization
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Import image processing
from PIL import Image

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="ATS Resume Analyzer PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
/* Main styles */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* Cards */
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-left: 5px solid #667eea;
    transition: transform 0.3s;
}
.metric-card:hover {
    transform: translateY(-5px);
}

/* Progress bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s;
}
.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0px 0px;
    padding: 10px 20px;
    font-weight: bold;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Text areas */
.stTextArea textarea {
    border-radius: 10px;
    border: 2px solid #e9ecef;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #667eea;
    border-radius: 10px;
    padding: 20px;
}

/* Success message */
.stAlert {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZE SESSION STATE ============
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

# ============ GROQ AI SETUP ============
def get_groq_client(api_key):
    """Create Groq client with API key"""
    try:
        return Groq(api_key=api_key.strip())
    except Exception as e:
        st.error(f"Error creating Groq client: {str(e)}")
        return None

# Available AI models
AVAILABLE_MODELS = {
    "⚡ Llama 3.1 8B (Fast & Free)": "llama-3.1-8b-instant",
    "🧠 Llama 3.3 70B (Most Accurate)": "llama-3.3-70b-versatile",
    "💎 Gemma 2 9B (Balanced)": "gemma2-9b-it",
    "🚀 Mixtral 8x22B (Expert)": "mixtral-8x22b-instruct"
}

# ============ PDF PROCESSING FUNCTIONS ============
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using multiple methods"""
    try:
        # Save uploaded file to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        text = ""
        
        # Method 1: Try pdfplumber (best for tables)
        try:
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                
                # Extract tables
                tables_found = []
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            tables_found.append(f"Table on page {i+1}: {len(table)} rows")
                
                if tables_found:
                    text += "\n\n[Detected " + str(len(tables_found)) + " tables in resume]\n"
        except:
            pass
        
        # Method 2: Try PyMuPDF for better extraction
        if len(text.strip()) < 100:  # If not enough text
            try:
                doc = fitz.open(tmp_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            except:
                pass
        
        # Method 3: Try PyPDF2 as last resort
        if len(text.strip()) < 100:
            try:
                uploaded_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            except:
                pass
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if len(text.strip()) > 50:
            return text[:5000]  # Limit to 5000 chars
        else:
            return "⚠️ Could not extract text. Please ensure PDF has selectable text (not scanned image)."
            
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def get_file_stats(uploaded_file):
    """Get statistics about the uploaded file"""
    stats = {
        'filename': uploaded_file.name,
        'size_mb': len(uploaded_file.getvalue()) / (1024 * 1024),
        'pages': 0
    }
    
    try:
        # Try to get page count
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            stats['pages'] = len(pdf.pages)
    except:
        try:
            doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            stats['pages'] = len(doc)
            doc.close()
        except:
            pass
    
    return stats

# ============ AI ANALYSIS FUNCTIONS ============
def analyze_with_ai(client, model, job_desc, resume_text, analysis_type):
    """Analyze resume with AI based on analysis type"""
    
    analysis_prompts = {
        "detailed": {
            "system": """You are an expert HR Director with 20+ years experience in tech recruitment.
            You analyze resumes against job descriptions with exceptional detail and accuracy.
            Always provide actionable, specific feedback.""",
            "user": f"""# COMPREHENSIVE RESUME ANALYSIS REPORT

## JOB DESCRIPTION ANALYSIS:
{job_desc[:2000]}

## RESUME CONTENT:
{resume_text[:2000]}

## PLEASE PROVIDE:

### 1. 🎯 EXECUTIVE SUMMARY
- Overall Match Score: [0-100]%
- One-line verdict
- Confidence level: High/Medium/Low

### 2. 📊 QUANTITATIVE ASSESSMENT
**Skills Match:**
- Technical Skills Alignment: [X/10]
- Soft Skills Match: [X/10]
- Tools & Technologies: [X/10]

**Experience Evaluation:**
- Years of Relevant Experience: [X] vs Required: [Y]
- Role Relevance: [X/10]
- Industry Experience: [X/10]

### 3. ✅ STRENGTHS IDENTIFIED
[List 5-7 specific strengths with examples from resume]

### 4. ⚠️ AREAS FOR IMPROVEMENT
[List 5-7 specific gaps with actionable solutions]

### 5. 🔑 KEYWORD ANALYSIS
- Top 10 Matching Keywords: [list]
- Top 10 Missing Keywords: [list]
- Keyword Density Score: [X/10]

### 6. 📈 ATS OPTIMIZATION SCORE: [0-100]
- Formatting: [X/10]
- Readability: [X/10]
- ATS Compliance: [X/10]

### 7. 🎯 HIRING PROBABILITY PREDICTION
- Pass ATS Screening: Yes/No/Maybe
- Likelihood of Interview: High/Medium/Low
- Estimated Shortlist Time: Immediate/1-3 days/1 week+

### 8. 💡 ACTIONABLE RECOMMENDATIONS
[Top 5 specific actions to improve resume]

### 9. 📝 COVER LETTER TIPS
[3 key points to highlight in cover letter]

### 10. 🎯 FINAL VERDICT & NEXT STEPS

Format with emojis, bold headings, and clear bullet points."""
        },
        
        "ats_score": {
            "system": """You are an ATS (Applicant Tracking System) algorithm expert.
            You analyze resumes strictly like an ATS would.
            Be objective, numerical, and data-driven.""",
            "user": f"""Generate ONLY a JSON response for ATS analysis:

JOB DESCRIPTION:
{job_desc[:1000]}

RESUME CONTENT:
{resume_text[:1000]}

Return this EXACT JSON structure:
{{
    "overall_score": 0-100,
    "breakdown": {{
        "keyword_match": 0-100,
        "experience_match": 0-100,
        "skills_match": 0-100,
        "education_match": 0-100,
        "formatting": 0-100,
        "readability": 0-100
    }},
    "prediction": {{
        "pass_ats": true/false,
        "interview_probability": "High/Medium/Low",
        "shortlist_time": "Immediate/1-3 days/1 week+"
    }},
    "keywords": {{
        "matched": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
        "missing": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
        "suggested": ["keyword1", "keyword2", "keyword3"]
    }},
    "improvements": [
        "Improvement 1",
        "Improvement 2", 
        "Improvement 3",
        "Improvement 4",
        "Improvement 5"
    ],
    "ats_optimization_tips": [
        "Tip 1",
        "Tip 2",
        "Tip 3"
    ]
}}"""
        },
        
        "cover_letter": {
            "system": """You are a professional cover letter writer specializing in tech roles.
            Write compelling, personalized cover letters that get interviews.""",
            "user": f"""Write a professional cover letter based on:

JOB DESCRIPTION:
{job_desc}

RESUME CONTENT:
{resume_text[:1500]}

Format:
1. Professional header with date and contact info
2. Appropriate salutation
3. Strong opening paragraph showing enthusiasm
4. 2-3 body paragraphs matching skills to job requirements
5. Specific examples from resume
6. Closing paragraph expressing interest
7. Professional sign-off

Make it:
- Specific to this job
- Confident but not arrogant
- 250-350 words
- Professional tone"""
        }
    }
    
    try:
        prompt = analysis_prompts[analysis_type]
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=1
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON if it's ATS score
        if analysis_type == "ats_score":
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return parsed
            except Exception as e:
                st.warning(f"Could not parse JSON: {str(e)}")
                # Return as text if parsing fails
                return result
        
        return result
        
    except Exception as e:
        st.error(f"AI Analysis Error: {str(e)}")
        return None

# ============ VISUALIZATION FUNCTIONS ============
def create_gauge_chart(score, title, color="#667eea"):
    """Create beautiful gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 24, 'color': color}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "#ff6b6b"},  # Red
                {'range': [40, 70], 'color': "#ffd93d"}, # Yellow
                {'range': [70, 100], 'color': "#6bcf7f"} # Green
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=100, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def create_radar_chart(scores_dict, title="Skills Breakdown"):
    """Create radar chart for skills"""
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],  # Close the shape
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
                rotation=90
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=16, color='#333')
        ),
        height=400,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_bar_chart(keywords, title, color="#667eea"):
    """Create horizontal bar chart for keywords"""
    df = pd.DataFrame({
        'Keywords': keywords[:10],  # Top 10
        'Count': [1] * min(10, len(keywords))  # Placeholder values
    })
    
    fig = px.bar(
        df, 
        y='Keywords', 
        x='Count',
        orientation='h',
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        xaxis={'showticklabels': False, 'title': ''},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ============ UI COMPONENTS ============
def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 3rem;">🚀 ATS Resume Analyzer PRO</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">AI-powered resume optimization • ATS compatibility check • Hiring probability prediction</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        # Logo/Header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>⚙️ Control Panel</h2>
            <p style="color: #666;">Configure your analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key Section
        st.subheader("🔑 API Configuration")
        api_key = st.text_input(
            "Groq API Key:",
            type="password",
            help="Get free API key from console.groq.com",
            value=st.session_state.get('api_key', '')
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key saved!")
            
            # Test API key
            if st.button("Test Connection", use_container_width=True):
                with st.spinner("Testing connection..."):
                    try:
                        client = get_groq_client(api_key)
                        if client:
                            st.success("✅ Connected successfully!")
                    except:
                        st.error("❌ Connection failed")
        else:
            st.warning("⚠️ Enter API key to continue")
        
        # API Key Help
        with st.expander("How to get FREE API Key"):
            st.markdown("""
            1. **Go to** [console.groq.com](https://console.groq.com)
            2. **Sign up** with email (free)
            3. **Navigate** to API Keys
            4. **Click** "Create API Key"
            5. **Copy** the key (starts with `gsk_`)
            6. **Paste** above
            7. **Free credits:** 30,000 tokens per minute
            """)
        
        st.markdown("---")
        
        # Model Selection
        st.subheader("🤖 AI Model")
        selected_model = st.selectbox(
            "Choose AI Model:",
            list(AVAILABLE_MODELS.keys()),
            index=0,
            help="Llama 3.1 8B is fastest for free tier"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("📈 Quick Stats")
        if st.session_state.analysis_history:
            total_analyses = len(st.session_state.analysis_history)
            avg_score = sum([a.get('score', 0) for a in st.session_state.analysis_history if 'score' in a]) / max(1, total_analyses)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Analyses", total_analyses)
            with col2:
                st.metric("Avg Score", f"{avg_score:.1f}%")
        else:
            st.info("No analyses yet")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear All", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        with col2:
            if st.button("📊 Demo Data", use_container_width=True):
                # Load demo data
                demo_job_desc = """Python Developer
                
Requirements:
- 3+ years Python experience
- Django/Flask framework knowledge
- REST API development
- SQL databases (PostgreSQL/MySQL)
- Git version control
- AWS/Azure cloud experience
- Docker containerization
- Unit testing (pytest)
- Agile/Scrum methodology
- Problem-solving skills

Responsibilities:
- Develop scalable web applications
- Write clean, maintainable code
- Collaborate with cross-functional teams
- Participate in code reviews
- Debug and optimize performance"""
                
                demo_resume = """John Doe
Senior Python Developer
john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe

SUMMARY
5+ years experience in Python development with expertise in Django, Flask, and cloud technologies. Proven track record of delivering scalable web applications.

EXPERIENCE
Senior Python Developer | Tech Solutions Inc. | 2020-Present
- Developed REST APIs using Django REST Framework serving 10,000+ requests/day
- Implemented microservices architecture reducing latency by 40%
- Led migration from monolithic to microservices architecture
- Mentored 3 junior developers

Python Developer | Startup XYZ | 2018-2020
- Built full-stack web applications using Flask and React
- Implemented CI/CD pipeline reducing deployment time by 60%
- Developed automated testing suite with 95% code coverage

SKILLS
Programming: Python, JavaScript, SQL
Frameworks: Django, Flask, React
Databases: PostgreSQL, MySQL, MongoDB
Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
Tools: Git, Jenkins, JIRA, pytest

EDUCATION
BS Computer Science | University of Technology | 2014-2018"""
                
                st.session_state.demo_job_desc = demo_job_desc
                st.session_state.demo_resume = demo_resume
                st.success("Demo data loaded!")
        
        return selected_model, api_key

# ============ MAIN APP FUNCTION ============
def main():
    """Main application function"""
    
    # Render header
    render_header()
    
    # Get sidebar configuration
    selected_model_name, api_key = render_sidebar()
    model_key = AVAILABLE_MODELS[selected_model_name]
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Upload", 
        "🔍 Analyze", 
        "📊 Dashboard", 
        "📈 Visualize", 
        "📚 History"
    ])
    
    # TAB 1: UPLOAD
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📁 Upload Resume")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose your resume (PDF format):",
                type=["pdf"],
                help="Upload your resume in PDF format. For best results, use text-based PDF (not scanned image)."
            )
            
            if uploaded_file:
                # Get file stats
                stats = get_file_stats(uploaded_file)
                
                # Display file info
                col1a, col2a, col3a = st.columns(3)
                with col1a:
                    st.metric("File Name", stats['filename'])
                with col2a:
                    st.metric("File Size", f"{stats['size_mb']:.2f} MB")
                with col3a:
                    st.metric("Pages", stats['pages'] if stats['pages'] > 0 else "N/A")
                
                # Extract text
                with st.spinner("📄 Extracting text from PDF..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.resume_text = resume_text
                
                # Preview
                with st.expander("📋 Preview Extracted Text", expanded=False):
                    if "⚠️" in resume_text or "Error" in resume_text:
                        st.warning(resume_text)
                    else:
                        st.text_area("", resume_text[:1500] + "...", height=300)
            
            st.markdown("---")
            
            # Job Description
            st.header("📝 Job Description")
            job_desc = st.text_area(
                "Paste the complete job description:",
                height=250,
                placeholder="Copy and paste the entire job description here...\n\nTip: Include requirements, responsibilities, and qualifications for best results.",
                value=st.session_state.get('demo_job_desc', '')
            )
            
            if job_desc:
                word_count = len(job_desc.split())
                st.caption(f"📊 {word_count} words | {len(job_desc)} characters")
            
            # Demo button
            if st.button("🎮 Load Demo Data", use_container_width=True):
                if 'demo_job_desc' in st.session_state:
                    st.rerun()
        
        with col2:
            st.header("⚡ Quick Start Guide")
            
            st.info("""
            ### 🎯 How to get best results:
            
            1. **Get API Key** (Free)
               - Sign up at Groq.com
               - Copy API key
               - Paste in sidebar
            
            2. **Upload Resume**
               - PDF format only
               - Text-based (not scanned)
               - Under 10MB size
            
            3. **Paste Job Description**
               - Copy from job posting
               - Include all requirements
               - Be specific
            
            4. **Choose Analysis Type**
               - Detailed: Complete report
               - ATS Score: Quick score
               - Cover Letter: AI-generated
            
            5. **Review & Improve**
               - Check missing keywords
               - Implement suggestions
               - Re-analyze
            """)
            
            st.markdown("---")
            
            # Status indicators
            st.subheader("✅ Ready Check")
            
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                st.metric("API", "✅" if api_key else "❌", 
                         "Configured" if api_key else "Required")
            
            with status_col2:
                st.metric("Resume", "✅" if uploaded_file else "❌", 
                         "Uploaded" if uploaded_file else "Required")
            
            with status_col3:
                st.metric("Job Desc", "✅" if job_desc else "❌", 
                         "Added" if job_desc else "Required")
    
    # TAB 2: ANALYZE
    with tab2:
        st.header("🔍 AI Analysis")
        
        if not api_key:
            st.warning("⚠️ Please enter your API key in the sidebar first!")
            st.stop()
        
        if not uploaded_file:
            st.warning("⚠️ Please upload your resume in the Upload tab!")
            st.stop()
        
        if not job_desc:
            st.warning("⚠️ Please paste a job description in the Upload tab!")
            st.stop()
        
        # Analysis type selection
        st.subheader("Choose Analysis Type:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            detailed_btn = st.button("📋 Detailed Analysis", 
                                   use_container_width=True,
                                   help="Complete report with scores, strengths, weaknesses, and recommendations")
        
        with col2:
            ats_btn = st.button("🎯 ATS Score & Keywords", 
                              use_container_width=True,
                              help="Quick ATS compatibility score with keyword analysis")
        
        with col3:
            cover_btn = st.button("📝 Generate Cover Letter", 
                                use_container_width=True,
                                help="AI-generated personalized cover letter")
        
        st.markdown("---")
        
        # Analysis results area
        analysis_result_placeholder = st.empty()
        
        # Handle analysis requests
        if detailed_btn or ats_btn or cover_btn:
            analysis_type = ""
            if detailed_btn:
                analysis_type = "detailed"
            elif ats_btn:
                analysis_type = "ats_score"
            else:
                analysis_type = "cover_letter"
            
            with st.spinner(f"🤖 Analyzing with {selected_model_name}..."):
                try:
                    # Get Groq client
                    client = get_groq_client(api_key)
                    
                    if not client:
                        st.error("Failed to create Groq client. Check API key.")
                        return
                    
                    # Get resume text
                    if not st.session_state.resume_text:
                        resume_text = extract_text_from_pdf(uploaded_file)
                    else:
                        resume_text = st.session_state.resume_text
                    
                    # Run analysis
                    result = analyze_with_ai(client, model_key, job_desc, resume_text, analysis_type)
                    
                    if result:
                        # Store in session state
                        analysis_data = {
                            "type": analysis_type,
                            "model": selected_model_name,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "filename": uploaded_file.name,
                            "job_desc_preview": job_desc[:100] + "...",
                            "result": result
                        }
                        
                        if analysis_type == "ats_score" and isinstance(result, dict):
                            analysis_data["score"] = result.get("overall_score", 0)
                        
                        st.session_state.current_analysis = analysis_data
                        st.session_state.analysis_history.append(analysis_data.copy())
                        
                        # Display success
                        st.success("✅ Analysis complete!")
                        
                        # Rerun to show results
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("Please check your API key and try again.")
        
        # Display current analysis if exists
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis
            
            with analysis_result_placeholder.container():
                st.markdown(f"### 📊 Analysis Results")
                st.caption(f"**Type:** {analysis['type'].title()} | **Model:** {analysis['model']} | **Time:** {analysis['timestamp']}")
                
                st.markdown("---")
                
                if analysis['type'] == "detailed":
                    st.markdown(analysis['result'])
                
                elif analysis['type'] == "ats_score":
                    if isinstance(analysis['result'], dict):
                        score_data = analysis['result']
                        
                        # Overall score
                        col_score1, col_score2 = st.columns([2, 1])
                        
                        with col_score1:
                            st.plotly_chart(
                                create_gauge_chart(
                                    score_data.get('overall_score', 0),
                                    "Overall ATS Score"
                                ),
                                use_container_width=True
                            )
                        
                        with col_score2:
                            prediction = score_data.get('prediction', {})
                            st.metric("ATS Prediction", 
                                     "✅ PASS" if prediction.get('pass_ats') else "❌ FAIL",
                                     prediction.get('interview_probability', ''))
                            
                            st.metric("Shortlist Time", 
                                     prediction.get('shortlist_time', 'N/A'))
                        
                        # Score breakdown
                        st.subheader("📈 Score Breakdown")
                        breakdown = score_data.get('breakdown', {})
                        
                        if breakdown:
                            cols = st.columns(len(breakdown))
                            for idx, (key, value) in enumerate(breakdown.items()):
                                with cols[idx]:
                                    progress = value / 100
                                    st.progress(progress)
                                    st.caption(f"**{key.replace('_', ' ').title()}**\n{value}%")
                        
                        # Keywords
                        st.subheader("🔑 Keyword Analysis")
                        keywords = score_data.get('keywords', {})
                        
                        col_kw1, col_kw2 = st.columns(2)
                        
                        with col_kw1:
                            if keywords.get('matched'):
                                st.markdown("#### ✅ Matching Keywords")
                                for kw in keywords['matched']:
                                    st.markdown(f"- `{kw}`")
                        
                        with col_kw2:
                            if keywords.get('missing'):
                                st.markdown("#### ❌ Missing Keywords")
                                for kw in keywords['missing']:
                                    st.markdown(f"- `{kw}`")
                        
                        # Improvements
                        st.subheader("💡 Improvement Suggestions")
                        improvements = score_data.get('improvements', [])
                        
                        for idx, imp in enumerate(improvements, 1):
                            st.markdown(f"{idx}. {imp}")
                        
                        # Tips
                        st.subheader("🎯 ATS Optimization Tips")
                        tips = score_data.get('ats_optimization_tips', [])
                        
                        for tip in tips:
                            st.info(f"💡 {tip}")
                    
                    else:
                        st.markdown(analysis['result'])
                
                elif analysis['type'] == "cover_letter":
                    st.markdown("### ✉️ AI-Generated Cover Letter")
                    st.markdown("---")
                    st.markdown(analysis['result'])
                
                # Download button
                st.markdown("---")
                
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                
                with col_dl1:
                    # Download report
                    if st.button("📥 Download Report", use_container_width=True):
                        report_content = f"""
                        ATS RESUME ANALYSIS REPORT
                        =========================
                        
                        Analysis Type: {analysis['type'].title()}
                        Date: {analysis['timestamp']}
                        AI Model: {analysis['model']}
                        Resume: {analysis['filename']}
                        
                        {'='*50}
                        
                        {analysis['result'] if isinstance(analysis['result'], str) else json.dumps(analysis['result'], indent=2)}
                        """
                        
                        st.download_button(
                            "Click to Download",
                            report_content,
                            file_name=f"ats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            key="download_report"
                        )
                
                with col_dl2:
                    if st.button("🔄 Run New Analysis", use_container_width=True):
                        st.session_state.current_analysis = None
                        st.rerun()
                
                with col_dl3:
                    if st.button("⭐ Save to History", use_container_width=True):
                        st.success("Saved to history!")
    
    # TAB 3: DASHBOARD
    with tab3:
        st.header("📊 Analysis Dashboard")
        
        if not st.session_state.current_analysis:
            st.info("👈 Run an analysis first to see the dashboard!")
        else:
            analysis = st.session_state.current_analysis
            
            if analysis['type'] == "ats_score" and isinstance(analysis['result'], dict):
                score_data = analysis['result']
                
                # Top metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall Score", 
                             f"{score_data.get('overall_score', 0)}%",
                             "ATS Compatibility")
                
                with col2:
                    prediction = score_data.get('prediction', {})
                    status = "✅ PASS" if prediction.get('pass_ats') else "❌ FAIL"
                    st.metric("ATS Status", status)
                
                with col3:
                    st.metric("Interview Chance", 
                             prediction.get('interview_probability', 'N/A'))
                
                with col4:
                    st.metric("Shortlist Time", 
                             prediction.get('shortlist_time', 'N/A'))
                
                st.markdown("---")
                
                # Visualizations
                col_viz1, col_viz2 = st.columns(2)
                
                with col_viz1:
                    # Gauge chart
                    st.plotly_chart(
                        create_gauge_chart(
                            score_data.get('overall_score', 0),
                            "ATS Compatibility Score"
                        ),
                        use_container_width=True
                    )
                
                with col_viz2:
                    # Radar chart for breakdown
                    breakdown = score_data.get('breakdown', {})
                    if breakdown:
                        st.plotly_chart(
                            create_radar_chart(breakdown, "Skills Breakdown"),
                            use_container_width=True
                        )
                
                # Keywords visualization
                st.subheader("🔤 Keyword Analysis")
                
                keywords = score_data.get('keywords', {})
                
                col_kw1, col_kw2 = st.columns(2)
                
                with col_kw1:
                    if keywords.get('matched'):
                        st.plotly_chart(
                            create_bar_chart(keywords['matched'], "✅ Matching Keywords"),
                            use_container_width=True
                        )
                
                with col_kw2:
                    if keywords.get('missing'):
                        st.plotly_chart(
                            create_bar_chart(keywords['missing'], "❌ Missing Keywords", "#ff6b6b"),
                            use_container_width=True
                        )
                
                # Improvement timeline
                st.subheader("📈 Improvement Roadmap")
                
                improvements = score_data.get('improvements', [])
                
                for idx, imp in enumerate(improvements, 1):
                    with st.expander(f"Step {idx}: {imp[:50]}..."):
                        st.info(f"**Action:** {imp}")
                        st.text_input(f"Your notes for Step {idx}", key=f"notes_{idx}")
                
            else:
                st.info("Dashboard available only for ATS Score analysis. Run an ATS Score analysis first.")
    
    # TAB 4: VISUALIZE
    with tab4:
        st.header("📈 Advanced Visualizations")
        
        if st.session_state.analysis_history:
            # History visualization
            scores = []
            dates = []
            
            for analysis in st.session_state.analysis_history:
                if analysis['type'] == "ats_score" and isinstance(analysis['result'], dict):
                    score = analysis['result'].get('overall_score', 0)
                    scores.append(score)
                    dates.append(analysis['timestamp'])
            
            if scores:
                # Create progress chart
                df = pd.DataFrame({
                    'Date': dates,
                    'Score': scores
                })
                
                fig = px.line(df, x='Date', y='Score', 
                            title='📈 Your ATS Score Progress',
                            markers=True,
                            line_shape='spline')
                
                fig.update_layout(
                    xaxis_title="Analysis Date",
                    yaxis_title="ATS Score (%)",
                    yaxis_range=[0, 100],
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Score distribution
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Average Score", f"{avg_score:.1f}%")
                
                with col_stat2:
                    st.metric("Best Score", f"{max_score}%")
                
                with col_stat3:
                    st.metric("Lowest Score", f"{min_score}%")
                
                with col_stat4:
                    st.metric("Total Analyses", len(scores))
            else:
                st.info("No ATS Score analyses found in history.")
        else:
            st.info("No analysis history yet. Run some analyses first!")
    
    # TAB 5: HISTORY
    with tab5:
        st.header("📚 Analysis History")
        
        if st.session_state.analysis_history:
            for idx, analysis in enumerate(reversed(st.session_state.analysis_history)):
                with st.expander(f"Analysis #{len(st.session_state.analysis_history)-idx} - {analysis['timestamp']}", expanded=False):
                    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
                    
                    with col_h1:
                        st.markdown(f"**Type:** {analysis['type'].title()}")
                        st.markdown(f"**Model:** {analysis['model']}")
                    
                    with col_h2:
                        st.markdown(f"**File:** {analysis['filename']}")
                    
                    with col_h3:
                        if analysis['type'] == "ats_score" and isinstance(analysis['result'], dict):
                            score = analysis['result'].get('overall_score', 0)
                            st.metric("Score", f"{score}%")
                    
                    st.markdown("**Job Description Preview:**")
                    st.caption(analysis['job_desc_preview'])
                    
                    st.markdown("---")
                    
                    if st.button(f"📋 Load This Analysis", key=f"load_{idx}"):
                        st.session_state.current_analysis = analysis
                        st.rerun()
                    
                    if st.button(f"🗑️ Delete This Analysis", key=f"delete_{idx}"):
                        # Find and remove
                        for i, a in enumerate(st.session_state.analysis_history):
                            if a['timestamp'] == analysis['timestamp']:
                                st.session_state.analysis_history.pop(i)
                                break
                        st.rerun()
        else:
            st.info("No analysis history yet. Your first analysis will appear here!")
    
    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 <strong>ATS Resume Analyzer PRO</strong> • Made with ❤️ using Streamlit & Groq AI</p>
        <p style="font-size: 0.9rem;">Disclaimer: AI analysis is for guidance only. Always verify with human review.</p>
    </div>
    """, unsafe_allow_html=True)

# ============ RUN THE APP ============
if __name__ == "__main__":
    main()