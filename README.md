# Resume AI: ATS Resume Builder + Reviewer

**Author:** [Akotur2005](https://github.com/Akotur2005)  
**Repository:** [https://github.com/Akotur2005/resume-ai](https://github.com/Akotur2005/resume-ai)

Stack: **React (Vite)** + **Python (Flask)** + **LangChain** + **PostgreSQL**

## What it does

1. **Builder**: fill a form and see a live ATS-safe resume (single column, plain text, standard headings). AI helps write the summary and polish bullet points. Save to Postgres. Print to PDF.
2. **Reviewer**: upload a PDF resume (and optionally a job description). You get an ATS score out of 100, a breakdown, issues with fixes, matched and missing keywords, and rewritten bullets.
3. **Import**: upload an old PDF into the builder. AI converts it to structured fields.

## Folder structure

```
resume-ai/
  backend/
    db/schema.sql              tables: resumes, reviews
    app.py                     Flask app
    db.py                      psycopg2 connection pool
    routes/resumes.py          CRUD + AI helpers (bullet, summary)
    routes/reviews.py          upload review, builder review, PDF import, history
    utils/pdf_utils.py         PDF -> text, resume JSON -> text
    chains/model.py            LangChain LLM client (Google Gemini)
    chains/review_chain.py     ATS scoring chain (Pydantic structured output)
    chains/builder_chain.py    bullet, summary, and PDF-parse chains
    requirements.txt           Python dependencies
  frontend/
    src/App.jsx                tabs
    src/api.js                 fetch wrapper
    src/components/ResumeBuilder.jsx
    src/components/ResumePreview.jsx
    src/components/ResumeReviewer.jsx
    src/components/ReviewResult.jsx
```

## Setup
 
```bash
# 1. Backend (Python + Flask)
cd resume-ai/backend
pip install -r requirements.txt
python app.py                 # API on http://localhost:5000

# 2. Frontend (React + Vite)
cd resume-ai/frontend
npm run dev                   # App on http://localhost:5173
```


## Project flow

### A. Reviewing an uploaded PDF
```
React (file + job description)
  -> POST /api/reviews/upload  (multer reads the file into memory)
  -> pdf-parse extracts plain text
  -> LangChain reviewChain: prompt -> LLM -> validated JSON (score, issues, keywords)
  -> INSERT into reviews table (PostgreSQL)
  -> JSON returned -> ReviewResult.jsx shows the report
```

### B. Building a resume
```
Form state (React) -> live ResumePreview (ATS layout)
  "AI improve" on a bullet  -> POST /api/resumes/ai/bullet  -> bulletChain
  "AI write" on the summary -> POST /api/resumes/ai/summary -> summaryChain
  Save   -> POST/PUT /api/resumes -> stored as JSONB in the resumes table
  Review -> POST /api/reviews/builder -> JSON -> text -> reviewChain -> saved in reviews
  Print  -> browser "Save as PDF" (text stays selectable, so ATS can read it)
```

### C. Importing an old PDF into the builder
```
PDF -> pdf-parse text -> parseChain (LangChain structured output) -> resume JSON -> form fields
```

## What is LangChain, and what does it do here?

LangChain is a framework that makes it easier to build apps around a large language model (LLM). Calling an LLM API directly gives you a string in and a string out. A real app needs more than that: prompt templates with variables, output you can trust to have a fixed shape, and the ability to chain steps together. LangChain provides these as building blocks.

The pieces used in this project:

| LangChain piece | Where | What it does for us |
|---|---|---|
| `ChatOpenAI` | `model.js` | One wrapper around the LLM. If you switch to another provider later, only this file changes. |
| `ChatPromptTemplate` | every chain | Reusable prompt with `{resume}` and `{jobDescription}` placeholders. Keeps the ATS rules in one place. |
| `.pipe()` (LCEL) | every chain | Connects steps: `prompt -> model -> parser`. Each step's output feeds the next. |
| `withStructuredOutput(zodSchema)` | `reviewChain.js`, `parseChain` | Forces the model to return JSON that matches our Zod schema (score, issues, keywords). No fragile regex parsing of text, so the React UI can rely on the shape. |
| `StringOutputParser` | bullet, summary chains | Turns the model's message object into a plain string. |

So in this project LangChain is the **AI orchestration layer**. Express handles HTTP and the database, React handles the UI, and LangChain turns "resume text + job description" into a reliable, structured ATS report.

Example: the review chain is just

```js
prompt.pipe(llm.withStructuredOutput(reviewSchema))
```

which reads as: fill the prompt, send it to the model, and return an object that matches `reviewSchema`.

## Why PostgreSQL

- `resumes.data` is **JSONB**, so the whole structured resume is stored in one column and you can add new sections without migrations.
- `reviews` stores every score with the original text and job description, so you can show score history and compare versions.

## ATS rules baked in

Single column, no tables or images, standard headings (Summary, Skills, Experience, Projects, Education), consistent dates, bullets that start with action verbs and include numbers, and keywords that mirror the job description.

## Ideas to extend

- User login (JWT) and a `user_id` column
- Embeddings + pgvector to rank resumes against many job descriptions
- Streaming responses for the review
- DOCX export

## Author

Developed by **[Akotur2005](https://github.com/Akotur2005)**
