# Resume AI - Python Flask + LangChain Backend

This is the Python backend for **Resume AI**, built with **Flask**, **LangChain**, and **PostgreSQL**. It handles all API endpoints, AI orchestration (powered by Google Gemini), PDF parsing, and database transactions.

---

## 🛠️ Tech Stack & Libraries
- **Framework:** Flask (Python REST API)
- **CORS:** Flask-CORS (Allows cross-origin requests from the React frontend on `:5173`)
- **AI Orchestration:** LangChain (`langchain-core`, `langchain-google-genai`)
- **LLM Provider:** Google Gemini (`gemini-2.5-flash`)
- **Data Validation:** Pydantic (Structured output enforcement)
- **Database:** PostgreSQL via `psycopg2` (Threaded connection pooling)
- **PDF Extraction:** `pypdf` (Fast, pure-Python selectable text extraction)

---

## 📡 API Endpoints

### 1. Resumes (`/api/resumes`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/resumes` | List all saved resumes (id, title, updated_at). |
| `GET` | `/api/resumes/<id>` | Fetch full structured resume JSON for a given ID. |
| `POST` | `/api/resumes` | Create and save a new resume (`title`, `data`). |
| `PUT` | `/api/resumes/<id>` | Update an existing resume's title or data. |
| `DELETE` | `/api/resumes/<id>` | Delete a resume. |
| `POST` | `/api/resumes/ai/bullet` | **AI Bullet Enhancer**: Rewrites a bullet with action verbs & metrics. |
| `POST` | `/api/resumes/ai/summary` | **AI Summary Generator**: Synthesizes experience and skills into a summary. |
| `POST` | `/api/resumes/ai/from-jd` | **AI Tailor from JD**: Crafts a full tailored resume from a job description. |

### 2. Reviews (`/api/reviews`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reviews/upload` | Upload a PDF resume (`multipart/form-data`) + optional job description to get an ATS review score & breakdown. |
| `POST` | `/api/reviews/builder` | Review a resume currently in the builder (using ID or inline data). |
| `POST` | `/api/reviews/import` | Upload a PDF resume to extract structured fields for the builder form. |
| `GET` | `/api/reviews` | Fetch recent review history (id, ats_score, created_at, source). |
| `GET` | `/api/reviews/<id>` | Fetch full diagnostic report and breakdown for a review. |

### 3. Health (`/api/health`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Returns `{"ok": true}` for API status checks. |

---

## ⚙️ Environment Variables (`.env`)

```env
PORT=5000
DATABASE_URL=postgres://postgres:password@localhost:5432/resume_ai
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
CLIENT_ORIGIN=http://localhost:5173
```

---

## 🚀 How to Run

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```powershell
   python app.py
   ```
   Server will start on **`http://localhost:5000`**.
