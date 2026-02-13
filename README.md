# 🚀 ATS Resume Analyser PRO

<div align="center">
  
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)
![Groq](https://img.shields.io/badge/Groq-API-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Deployment](https://img.shields.io/badge/Deployment-Streamlit%20Cloud-brightgreen.svg)

**AI-Powered Resume Optimization Tool | ATS Compatibility Check | Smart Career Assistant**

[Live Demo](https://ats-resume-analyser-pro-chqbtqrmwxyv6fyvnbvnss.streamlit.app/) • [Report Bug](https://github.com/your-username/ats-analyzer/issues) • [Request Feature](https://github.com/your-username/ats-analyzer/issues)

</div>

---

## 📋 **Table of Contents**
- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Demo](#demo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Features in Detail](#features-in-detail)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

---

## 🎯 **About The Project**

ATS Resume Analyzer PRO is an advanced AI-powered web application that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). In today's competitive job market, over 75% of resumes are rejected by ATS before reaching human eyes. This tool bridges that gap by providing instant, actionable feedback on how well your resume matches job descriptions.

**The Problem:**
- Most resumes never get seen by recruiters due to ATS filters
- Job seekers don't know which keywords to include
- Manual resume optimization is time-consuming and subjective

**The Solution:**
- AI-powered analysis using Groq's Llama 3.1 model
- Instant ATS compatibility scoring
- Detailed keyword gap analysis
- Actionable improvement suggestions

---

## ✨ **Key Features**

### 🔍 **Smart Analysis**
- **Multi-Mode Analysis**: Choose from Detailed Analysis, ATS Score, or Cover Letter Generation
- **Real-time Processing**: Get results in under 30 seconds
- **Semantic Matching**: AI understands context, not just keywords

### 📊 **ATS Compatibility**
- **Percentage Score**: Instant match rating (0-100%)
- **Keyword Analysis**: Identify matching and missing keywords
- **Formatting Check**: Ensure ATS-friendly formatting

### 💼 **Career Tools**
- **Cover Letter Generator**: AI-crafted personalized cover letters
- **Improvement Roadmap**: Step-by-step action plan
- **History Tracking**: Save and compare multiple analyses

### 📈 **Visual Analytics**
- **Interactive Charts**: Gauge, radar, and bar charts for easy understanding
- **Progress Tracking**: Monitor improvement over time
- **Export Reports**: Download analysis as text files

### 🛡️ **Professional Features**
- **Multi-PDF Support**: Handles various PDF formats
- **Dark Mode Compatible**: Works in both light and dark themes
- **Session Management**: Saves analysis history during session

---

## 🛠️ **Tech Stack**

### **Core Technologies**
| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Primary programming language |
| **Streamlit** | Web application framework |
| **Groq AI** | Large Language Model API (Llama 3.1) |
| **Plotly** | Interactive data visualization |
| **Pandas** | Data manipulation and analysis |

### **PDF Processing**
| Library | Purpose |
|---------|---------|
| **PyPDF2** | Basic PDF text extraction |
| **pdfplumber** | Advanced PDF parsing with table support |
| **PyMuPDF (fitz)** | High-performance PDF processing |
| **Pillow** | Image processing for scanned PDFs |

### **Deployment & DevOps**
| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **GitHub** | Code repository |
| **Streamlit Cloud** | Hosting and deployment |
| **VS Code** | Development environment |

### **Additional Libraries**
- `python-dotenv` - Environment variable management
- `openpyxl` - Excel file support
- `json` - Data serialization
- `datetime` - Timestamp management

---

## 🎥 **Demo**

### **Live Application**
🔗 **[https://ats-analyzer-pro.streamlit.app](https://your-app-name.streamlit.app)**

### **Quick Walkthrough**

<details>
<summary>📹 Click to see demo steps</summary>

1. **Enter API Key** - Paste your free Groq API key
2. **Upload Resume** - Choose your PDF resume
3. **Paste Job Description** - Copy from job posting
4. **Choose Analysis Type** - Detailed, ATS Score, or Cover Letter
5. **Get Results** - Receive instant AI analysis
6. **Download Report** - Save analysis for future reference

</details>

---

## 🚀 **Getting Started**

### **Prerequisites**

Before you begin, ensure you have:
- ✅ Python 3.9 or higher installed
- ✅ Git installed
- ✅ Groq API key (free from [console.groq.com](https://console.groq.com))
- ✅ Basic understanding of command line

### **Installation**

#### **Option 1: Quick Install (Recommended)**

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ats-analyzer.git
   cd ats-analyzer
