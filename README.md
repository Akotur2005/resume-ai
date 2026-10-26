# Resume AI: ATS Resume Builder + Reviewer

**Author:** [Akotur2005](https://github.com/Akotur2005)  
**Repository:** [https://github.com/Akotur2005/resume-ai](https://github.com/Akotur2005/resume-ai)  
**Stack:** React (Vite) + Python (Flask) + LangChain + Google Gemini + PostgreSQL

---

## 📌 Problem & Purpose

Over **75% of resumes are rejected by Applicant Tracking Systems (ATS)** before reaching a hiring manager. Most rejections stem from:
1. **Formatting Failures:** Complex multi-column templates, tables, graphics, text boxes, and icons that confuse parsing algorithms.
2. **Keyword Deficits:** Missing crucial technical skills, domain keywords, and measurable impact verbs demanded by the job description.

**Resume AI** solves this by providing a dual-engine platform:
- **An ATS-Safe Builder** to write, structure, and live-preview resumes that conform 100% to strict ATS formatting rules.
- **An ATS Reviewer & Scorer** powered by **LangChain** and **Google Gemini** to evaluate any PDF resume against a job description, delivering a score out of 100, keyword match analytics, prioritized fixes, and rewritten bullet points.

---

## 🚀 Key Features in Detail

### 1. ATS Resume Builder (Live Editor & AI Co-Pilot)
- **Real-Time ATS-Safe Preview:** A single-column, standard-heading live preview renders in real time side-by-side with your form.
- **AI Bullet Enhancer (`POST /api/resumes/ai/bullet`):**
  - Transforms weak bullets (e.g., *"helped make website faster"*) into recruiter-ready achievements.
  - Applies the proven ATS formula: **Action Verb + Task/Scope + Tool/Technology + Quantifiable Outcome (`[X%]`)**.
- **AI Summary Generator (`POST /api/resumes/ai/summary`):**
  - Analyzes target roles, skills, and past work history to generate a 3-sentence professional summary in first-person-implied style (no "I").
- **AI Tailor from Job Description (`POST /api/resumes/ai/from-jd`):**
  - Generates a fully tailored ATS resume matching a pasted job description and candidate background notes.
- **Database Persistence:** Save, load, update, and manage multiple resumes directly in PostgreSQL (`JSONB`).
- **Clean PDF Export:** Print-optimized layout (`@media print`) generating clean, selectable-text PDFs without headers or footers.

### 2. ATS Resume Reviewer (Diagnostic Engine)
- **PDF Upload & Analysis (`POST /api/reviews/upload`):** Upload any existing PDF resume alongside an optional target job description.
- **Overall ATS Score (0 - 100):** Comprehensive score calculated by evaluating your resume against ATS rules.
- **5-Category Breakdown (0 - 100 each):**
  - **Formatting:** Single-column integrity, readable dates, no tables/graphics.
  - **Keywords:** Keyword density and match rate against the job description.
  - **Sections:** Standard headings (Summary, Experience, Education, Skills, Projects, Certifications).
  - **Impact:** Frequency of quantified achievements, percentages, metrics, and strong action verbs.
  - **Readability:** Sentence structure, conciseness, and bullet formatting.
- **Keyword Match Analytics:**
  - **Matched Keywords:** Skills and tools already found on your resume.
  - **Missing Keywords:** Crucial technical and domain keywords from the JD that your resume is missing.
- **Prioritized Issues & Fixes:** Pinpoints issues with a severity rating (**High**, **Medium**, **Low**) and gives exact advice on how to fix them.
- **Rewritten Bullets:** Takes up to 5 of your weakest bullets and returns polished, high-impact replacements.
- **Score History (`GET /api/reviews`):** Tracks your audit history over time to measure improvement.

### 3. PDF Resume Importer (`POST /api/reviews/import`)
- Upload an existing PDF resume to auto-fill the builder form.
- Python's `pypdf` extracts the raw text.
- LangChain analyzes the content and extracts structured data (contact info, skills, experience, projects, education) to populate the builder form instantly.

---

## 🛠️ System Architecture

```
┌────────────────────────────────┐
│   React + Vite Frontend (UI)   │  Port 5173
│  Forms, Live Preview, Scoring  │
└───────────────┬────────────────┘
                │ HTTP REST Calls (Proxied /api)
┌───────────────▼────────────────┐
│   Python Flask Backend (API)   │  Port 5000
│  Routes, CORS, File Uploads    │
└───────┬────────────────┬───────┘
        │                │
┌───────▼──────┐  ┌──────▼───────────────────────────┐
│  PostgreSQL  │  │   LangChain AI Orchestration     │
│  Data Store  │  │  Prompt -> Gemini LLM -> Pydantic │
└──────────────┘  └──────────────────────────────────┘
```

---

## 📁 Folder Structure

```
resume-ai/
  backend/
    app.py                     Flask REST API application
    db.py                      psycopg2 threaded PostgreSQL pool
    chains/
      model.py                 LangChain Gemini client (gemini-2.5-flash)
      review_chain.py          ATS scoring chain with Pydantic schema
      builder_chain.py         Bullet, summary, parser, and JD chains
    routes/
      resumes.py               CRUD + AI helpers (bullet, summary, from-jd)
      reviews.py               Upload review, builder review, PDF import, history
    utils/
      pdf_utils.py             pypdf text extraction & resume-to-text converter
    db/
      schema.sql               Database tables: resumes, reviews, resume_vectors
    requirements.txt           Python dependencies
    .env.example               Environment variable template
  frontend/
    src/
      App.jsx                  Main tabs & application layout
      api.js                   Fetch API wrapper
      components/
        ResumeBuilder.jsx      Interactive form + live preview layout
        ResumePreview.jsx      ATS single-column resume preview
        ResumeReviewer.jsx     PDF upload & review submission
        ReviewResult.jsx       ATS score report & keyword dashboard
```

---

## 🧠 LangChain AI Orchestration

LangChain serves as the **AI orchestration layer**, connecting prompts to Google Gemini and parsing outputs into validated Pydantic models:

| Component | File | Role |
|---|---|---|
| `ChatGoogleGenerativeAI` | `chains/model.py` | Google Gemini model client (`gemini-2.5-flash`). |
| `ChatPromptTemplate` | All chains | Reusable prompt templates containing strict ATS guidelines. |
| `|` (LCEL Pipe) | All chains | Modern LangChain Expression Language connecting prompt, model, and parser. |
| `with_structured_output` | `review_chain.py`, `builder_chain.py` | Forces the LLM to return strictly validated Pydantic data schemas (`ReviewSchema`, `ResumeSchema`). |
| `StrOutputParser` | `builder_chain.py` | Parses free-text LLM responses for bullet points and summaries. |

---

## 💾 Database Design (PostgreSQL)

- **`resumes` table (`JSONB`):** Entire resume structure is stored in a single `data` column using `JSONB`, allowing dynamic fields without requiring SQL migrations.
- **`reviews` table:** Stores audit histories, overall ATS score, category breakdowns, and timestamped reports.
- **`resume_vectors` table:** Prepared with `vector(1536)` for semantic similarity search with `pgvector`.

---

## ⚙️ Setup & Installation

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **PostgreSQL** (v14+)

### 1. Database Setup
```bash
createdb resume_ai
psql -d resume_ai -f backend/db/schema.sql
```

### 2. Backend Setup (Python Flask)
```powershell
cd resume-ai/backend
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env

# Run the API server
python app.py
```
*API will be running on **http://localhost:5000**.*

### 3. Frontend Setup (React Vite)
```powershell
cd resume-ai/frontend
npm install

# Run the development server
npm.cmd run dev
```
*Application will be running on **http://localhost:5173**.*

---

## 📄 License & Credits

Developed by **[Akotur2005](https://github.com/Akotur2005)**.
Open-source under the MIT License.
