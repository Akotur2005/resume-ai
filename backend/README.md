# Resume AI - Python Flask + LangChain Backend

This is the Python implementation of the Resume AI backend using **Flask**, **LangChain**, and **PostgreSQL**. It serves as a 100% compatible drop-in replacement for the Node.js backend.

## Tech Stack
- **Flask**: Lightweight REST API framework
- **Flask-CORS**: Cross-origin resource sharing for the React frontend
- **LangChain**: AI orchestration layer (`langchain-core`, `langchain-google-genai`)
- **Google Gemini**: LLM model (`gemini-2.5-flash`)
- **psycopg2**: PostgreSQL driver
- **pypdf**: PDF text extraction

## Endpoints
- `GET /api/health`: Health check
- `GET /api/resumes`: List saved resumes
- `GET /api/resumes/<id>`: Get single resume
- `POST /api/resumes`: Create resume
- `PUT /api/resumes/<id>`: Update resume
- `DELETE /api/resumes/<id>`: Delete resume
- `POST /api/resumes/ai/bullet`: AI bullet point optimizer (LangChain)
- `POST /api/resumes/ai/summary`: AI professional summary generator (LangChain)
- `POST /api/resumes/ai/from-jd`: AI full tailored resume generator from Job Description (LangChain)
- `POST /api/reviews/upload`: Review PDF resume with ATS scoring (LangChain)
- `POST /api/reviews/builder`: Review resume built in builder (LangChain)
- `POST /api/reviews/import`: Import PDF resume into structured builder JSON (LangChain)
- `GET /api/reviews`: Review history
- `GET /api/reviews/<id>`: Get review details

## How to Run
```powershell
cd backend
python app.py
```

API runs on `http://localhost:5000`.
