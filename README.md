# Resume AI: ATS Resume Builder and Reviewer

A full-stack web application designed to generate, format, score, and optimize resumes for Applicant Tracking Systems (ATS). The application pairs an ATS-compliant resume builder with an AI-driven review engine powered by LangChain, Google Gemini, Python (Flask), React, and PostgreSQL.

---

## Project Overview

Modern hiring pipelines rely heavily on Applicant Tracking Systems (ATS) such as Workday, Taleo, Greenhouse, Lever, and iCIMS to automatically parse and filter applicant resumes before human review. Industry data indicates that more than 75% of candidate resumes are filtered out due to structural parsing errors (e.g., complex multi-column grids, tables, non-standard headers, unparseable graphics) or low semantic alignment with target job descriptions.

Resume AI provides a complete end-to-end solution:
1. **ATS Resume Builder:** Enables candidates to construct and live-preview resumes strictly formatted to standard ATS guidelines (single-column, standard headings, machine-readable date ranges, selectable text). Built-in AI assistants polish bullet points, draft professional summaries, and tailor resumes directly from job descriptions.
2. **ATS Resume Reviewer:** Ingests any PDF resume and optional job description, parses the raw selectable text, and runs an automated ATS compliance audit. It calculates an overall ATS score (0-100), provides category-specific scoring breakdowns, highlights matched and missing keywords, flags prioritized formatting and content issues, and generates rewritten bullet points with action verbs and quantifiable metrics.
3. **Resume Importer:** Parses existing PDF resumes into structured JSON fields using LLM-based entity extraction, instantly populating the builder without manual data entry.

---

## Core Features and Workflows

### 1. ATS Resume Builder
The builder interface provides a structured form on the left with a synchronized, real-time preview on the right.

- **Real-Time Compliant Preview:** Renders an ATS-safe layout using single-column flow, plain typography, standard section titles, and zero visual artifacts (no tables, floating text boxes, or graphical charts).
- **AI Bullet Point Optimizer (`POST /api/resumes/ai/bullet`):**
  - Upgrades unstructured or passive bullet points into high-impact accomplishment statements.
  - Enforces the recruiter standard: **Action Verb + Core Responsibility/Task + Tech Stack/Tools + Quantifiable Outcome (`[X%]`)**.
  - Restricts length to under 25 words to prevent ATS line-wrapping and truncation issues.
- **AI Professional Summary Generator (`POST /api/resumes/ai/summary`):**
  - Synthesizes the candidate's target job title, core skill set, and work history into a concise 3-sentence summary written in standard first-person-implied style (omitting personal pronouns like "I" or "my").
- **Job Description Tailoring (`POST /api/resumes/ai/from-jd`):**
  - Accepts a raw job description and optional candidate notes, outputting a fully structured, keyword-optimized resume matching the requirements of the specified role.
- **Data Persistence:** Resumes can be saved, edited, listed, and deleted via PostgreSQL database storage.
- **Print and Export:** Fully optimized CSS print stylesheets (`@media print`) format the resume for standard Letter/A4 printing with selectable text suitable for direct job application uploads.

### 2. ATS Resume Reviewer
The reviewer accepts uploaded PDF resumes and evaluates their quality and compatibility against target roles.

- **Text Extraction:** Uses `pypdf` to extract underlying text layers while verifying that the PDF is machine-readable rather than a scanned image.
- **Overall ATS Score (0 to 100):** A normalized score reflecting the resume's structural readability and keyword alignment.
- **5-Category Scoring Breakdown:**
  - **Formatting (0-100):** Evaluates layout single-column compliance, date format consistency, and heading hierarchy.
  - **Keywords (0-100):** Measures keyword coverage and semantic similarity relative to the target job description.
  - **Sections (0-100):** Verifies the presence of required headings (Summary, Skills, Experience, Education, Projects, Certifications).
  - **Impact (0-100):** Assesses the presence of action-oriented verbs, metrics, percentages, and quantifiable achievements.
  - **Readability (0-100):** Evaluates sentence structure, brevity, and bullet length.
- **Keyword Analytics:**
  - **Matched Keywords:** Core technical skills, frameworks, and methodologies detected in both the resume and the job description.
  - **Missing Keywords:** Required or high-priority skills found in the job description that are absent from the resume.
- **Prioritized Issues & Fixes:** Each identified issue is classified by severity (`High`, `Medium`, `Low`) with an actionable recommendation for resolution.
- **Bullet Rewrites:** Automatically identifies up to 5 weak bullet points from the resume and provides ready-to-use rewritten alternatives.
- **Audit History:** Review results are logged to PostgreSQL, allowing candidates to track scoring progress across successive revisions.

### 3. PDF Resume Importer
- **Automated Structuring (`POST /api/reviews/import`):** Extracts raw text from an existing resume PDF and passes it through a structured extraction chain.
- **Schema Mapping:** Maps free-form text into strict JSON objects representing personal contact details, categorized skills, employment history, education, projects, and certifications.
- **Form Auto-Population:** Directly feeds the parsed JSON into the React builder state, saving time during onboarding.

---

## System Architecture

```
┌────────────────────────────────────────┐
│        React + Vite Frontend           │  Port 5173
│  Form State, Live Preview, Diagnostics │
└───────────────────┬────────────────────┘
                    │ HTTP REST Requests (Proxied /api)
┌───────────────────▼────────────────────┐
│         Flask API (Python Backend)     │  Port 5000
│  Routes, CORS, File Uploads, Validation│
└─────────┬──────────────────────┬───────┘
          │                      │
┌─────────▼────────────┐  ┌──────▼────────────────────────────────┐
│      PostgreSQL      │  │      LangChain Orchestration Layer    │
│  Resumes, Reviews,   │  │  LCEL Chains, Google Gemini LLM,     │
│  Vector Embeddings   │  │  Pydantic Structured Output Models    │
└──────────────────────┘  └───────────────────────────────────────┘
```

---

## Technical Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite | Component architecture, form management, real-time live preview |
| **Backend** | Python, Flask, Flask-CORS | REST API routing, CORS handling, multipart file uploads |
| **AI Orchestration** | LangChain, LangChain Core | LCEL prompt chaining, model abstraction, structured parsing |
| **LLM Provider** | Google Gemini (`gemini-2.5-flash`) | Natural language processing, scoring, and text generation |
| **Schema Validation**| Pydantic v2 | Strict JSON schema definitions for model responses |
| **PDF Processing** | `pypdf` | Server-side text extraction from PDF documents |
| **Database** | PostgreSQL, `psycopg2` | Relational storage, JSONB document fields, connection pooling |

---

## LangChain and LLM Implementation Details

LangChain serves as the AI orchestration engine, decoupling business logic from raw API calls:

1. **Model Wrapper (`chains/model.py`):**
   - Configures `ChatGoogleGenerativeAI` with a temperature setting of `0.2` for deterministic, reliable evaluations.
   - Credentials are read directly from the `.env` configuration (`GEMINI_API_KEY`, `GEMINI_MODEL`).

2. **Structured Outputs with Pydantic:**
   - Rather than relying on fragile string parsing or regex, chains leverage `llm.with_structured_output(...)` backed by explicit Pydantic schemas:
     - `ReviewSchema`: Defines fields for `atsScore`, `breakdown`, `summary`, `strengths`, `issues` (with severity levels), `matchedKeywords`, `missingKeywords`, and `rewrittenBullets`.
     - `ResumeSchema`: Defines structured entities for contact information, experience items, education entries, project listings, and skills arrays.

3. **LangChain Expression Language (LCEL):**
   - Pipelines are assembled via declarative LCEL pipes:
     ```python
     # Example: ATS Review Pipeline
     review_chain = prompt | llm.with_structured_output(ReviewSchema)

     # Example: Bullet Optimization Pipeline
     bullet_chain = bullet_prompt | llm | StrOutputParser()
     ```

---

## Database Design

PostgreSQL is configured with three primary tables:

1. **`resumes`:**
   - `id`: Auto-incrementing primary key.
   - `title`: User-defined resume label.
   - `data`: Complete structured resume stored as a native `JSONB` document, enabling dynamic section additions without requiring schema migrations.
   - `created_at`, `updated_at`: Timestamps for version tracking.

2. **`reviews`:**
   - `id`: Auto-incrementing primary key.
   - `resume_id`: Optional foreign key reference to `resumes(id)`.
   - `source`: Indicator of review origin (`upload` vs. `builder`).
   - `file_name`: Original uploaded document filename.
   - `resume_text`: Plain text extracted from the document.
   - `job_description`: Target role description used for keyword evaluation.
   - `ats_score`: Integer rating (0-100).
   - `result`: Full Pydantic feedback report stored as `JSONB`.
   - `created_at`: Timestamp.

3. **`resume_vectors`:**
   - Designed for semantic resume-to-job matching using PostgreSQL's `pgvector` extension and HNSW indexing.

---

## API Reference

### Resumes (`/api/resumes`)
- `GET /api/resumes`: Returns a summary list of all stored resumes.
- `GET /api/resumes/<id>`: Returns the full document object for a specific resume.
- `POST /api/resumes`: Saves a new resume document.
- `PUT /api/resumes/<id>`: Updates existing resume fields.
- `DELETE /api/resumes/<id>`: Deletes a stored resume.
- `POST /api/resumes/ai/bullet`: Rewrites an individual bullet point for ATS impact.
- `POST /api/resumes/ai/summary`: Generates a professional summary from structured resume data.
- `POST /api/resumes/ai/from-jd`: Generates a tailored resume from a provided job description.

### Reviews (`/api/reviews`)
- `POST /api/reviews/upload`: Ingests a PDF file via multipart upload and evaluates it against an optional job description.
- `POST /api/reviews/builder`: Runs an ATS evaluation on data currently held in the builder interface.
- `POST /api/reviews/import`: Extracts text from an uploaded PDF and maps it into builder form fields.
- `GET /api/reviews`: Returns past review history.
- `GET /api/reviews/<id>`: Returns full diagnostic results for a past review.

### Health Check (`/api/health`)
- `GET /api/health`: Returns service operational status (`{"ok": true}`).

---

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+

### 1. Database Initialization
```bash
createdb resume_ai
psql -d resume_ai -f backend/db/schema.sql
```

### 2. Backend Setup
```powershell
cd backend
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run the Flask API server
python app.py
```
The API server listens on `http://localhost:5000`.

### 3. Frontend Setup
```powershell
cd frontend
npm install

# Start the Vite development server
npm.cmd run dev
```
The client interface is accessible at `http://localhost:5173`.

---

## Running with Docker (Recommended)

The entire full-stack application (PostgreSQL + pgvector, Flask Backend, and React Frontend with Nginx) can be launched with a single Docker Compose command:

### 1. Configure Environment
Set your Gemini API key in `.env`:
```bash
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

### 2. Start Containers
```bash
docker compose up --build
```

### 3. Access Application
- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:5000`
- **PostgreSQL Database:** `localhost:5432` (database: `resume_ai`, user: `postgres`, password: `postgres`)

To stop the services:
```bash
docker compose down
```

