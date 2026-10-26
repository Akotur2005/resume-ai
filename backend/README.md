# Resume AI Backend: Flask and LangChain Service

The backend service for Resume AI is implemented using Python, Flask, LangChain, Google Gemini, and PostgreSQL. It exposes a RESTful API for resume management, automated ATS scoring, AI content generation, and document parsing.

---

## Technical Specifications
- **Application Framework:** Flask (WSGI Web Framework)
- **CORS Handling:** Flask-CORS (Allows cross-origin communication with Vite frontend on port 5173)
- **AI Orchestration:** LangChain (`langchain-core`, `langchain-google-genai`)
- **Language Model:** Google Gemini (`gemini-2.5-flash`)
- **Data Validation:** Pydantic v2 (Strict schema compliance for structured outputs)
- **Database Layer:** PostgreSQL accessed via `psycopg2` with threaded connection pooling
- **Document Processing:** `pypdf` (Text extraction from PDF byte streams)

---

## API Endpoints

### 1. Resumes (`/api/resumes`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/resumes` | Retrieves an array of all saved resumes (`id`, `title`, `updated_at`). |
| `GET` | `/api/resumes/<id>` | Retrieves the full structured resume JSON for a specified identifier. |
| `POST` | `/api/resumes` | Inserts a new resume document (`title`, `data`). |
| `PUT` | `/api/resumes/<id>` | Updates the title or content payload of an existing resume. |
| `DELETE` | `/api/resumes/<id>` | Deletes the specified resume record. |
| `POST` | `/api/resumes/ai/bullet` | Generates an optimized, action-verb-driven bullet point with metrics. |
| `POST` | `/api/resumes/ai/summary` | Synthesizes role, skills, and history into a 3-sentence summary. |
| `POST` | `/api/resumes/ai/from-jd` | Creates an ATS-tailored resume directly from a provided job description. |

### 2. Reviews (`/api/reviews`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reviews/upload` | Ingests a PDF resume (`multipart/form-data`) and evaluates it against an optional job description. Returns the overall ATS score, breakdown, issues, and keyword analytics. |
| `POST` | `/api/reviews/builder` | Evaluates a resume currently in the builder without requiring PDF export. |
| `POST` | `/api/reviews/import` | Extracts text from an uploaded PDF resume and maps it into structured builder fields. |
| `GET` | `/api/reviews` | Retrieves a list of recent review summaries. |
| `GET` | `/api/reviews/<id>` | Retrieves the complete evaluation report for a specific review. |

### 3. Health Check (`/api/health`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Returns service health status (`{"ok": true}`). |

---

## Environment Configuration (`.env`)

Configure the following variables in a `.env` file located in this directory:

```env
PORT=5000
DATABASE_URL=postgres://postgres:password@localhost:5432/resume_ai
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
CLIENT_ORIGIN=http://localhost:5173
```

---

## Running the Service

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the API:**
   ```powershell
   python app.py
   ```
   The service listens on `http://localhost:5000`.
