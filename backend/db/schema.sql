-- Run: createdb resume_ai && psql "$DATABASE_URL" -f db/schema.sql

CREATE TABLE IF NOT EXISTS resumes (
  id          SERIAL PRIMARY KEY,
  title       TEXT NOT NULL DEFAULT 'My Resume',
  data        JSONB NOT NULL,              -- full structured resume (see frontend/src/emptyResume.js)
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
  id               SERIAL PRIMARY KEY,
  resume_id        INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
  source           TEXT NOT NULL CHECK (source IN ('builder', 'upload')),
  file_name        TEXT,
  resume_text      TEXT NOT NULL,
  job_description  TEXT,
  ats_score        INTEGER NOT NULL CHECK (ats_score BETWEEN 0 AND 100),
  result           JSONB NOT NULL,         -- full structured AI feedback
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reviews_resume_id ON reviews(resume_id);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC);

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Store resume embeddings for similarity search
CREATE TABLE IF NOT EXISTS resume_vectors (
  id          SERIAL PRIMARY KEY,
  resume_id   INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
  content     TEXT NOT NULL,
  embedding   vector(1536),           -- 1536 dimensions for OpenAI text-embedding-3-small
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_resume_vectors_embedding 
ON resume_vectors USING hnsw (embedding vector_cosine_ops);

