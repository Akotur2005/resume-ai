import json
from typing import List, Dict, Optional
from db import query
from chains.model import embeddings

DEFAULT_EXEMPLAR_BULLETS = [
    "Spearheaded redesign of cloud-native microservices architecture using Python and Docker, reducing API latency by 38% and saving $45,000 in monthly infrastructure costs.",
    "Architected automated CI/CD deployment pipelines using GitHub Actions and Kubernetes, accelerating release cadence from bi-weekly to multiple daily zero-downtime deployments.",
    "Engineered distributed PostgreSQL database indexing and query caching strategies with Redis, improving p99 response times by 45% under 100k daily active users.",
    "Led cross-functional team of 6 engineers to build real-time analytics dashboard with React, FastAPI, and WebSocket, increasing customer engagement by 27%.",
    "Developed high-throughput data processing pipelines in Apache Kafka and AWS Lambda, processing over 10M records daily with 99.99% data pipeline uptime.",
    "Integrated machine learning fraud detection models into payment processing pipeline, reducing fraudulent transaction chargebacks by 34% within 90 days.",
    "Automated end-to-end integration and load testing suites, increasing unit test code coverage from 55% to 92% across all mission-critical microservices.",
    "Implemented role-based access control (RBAC) and OAuth2/OIDC authentication protocols, achieving SOC2 Type II compliance approval with zero audit deficiencies.",
    "Designed scalable RESTful and GraphQL APIs serving 15M+ monthly requests, maintaining 99.95% SLA and sub-50ms median response times.",
    "Optimized frontend bundle size and critical rendering path in React/Vite, cutting initial page load times by 52% and boosting conversion rate by 14%."
]

def format_vector(vector: List[float]) -> str:
    """Formats float list to PostgreSQL pgvector literal: '[0.1, 0.2, ...]'"""
    return "[" + ",".join(str(float(x)) for x in vector) + "]"

def store_embedding(content: str, category: str = "resume_chunk", resume_id: Optional[int] = None) -> Optional[int]:
    """Generates embedding via LangChain and stores it in PostgreSQL resume_vectors table."""
    try:
        vector = embeddings.embed_query(content)
        vector_str = format_vector(vector)
        sql = """
            INSERT INTO resume_vectors (resume_id, category, content, embedding)
            VALUES (%s, %s, %s, %s::vector) RETURNING id
        """
        row = query(sql, [resume_id, category, content, vector_str], fetch_one=True, commit=True)
        return row["id"] if row else None
    except Exception as e:
        print(f"[VectorStore] Warning: Failed to store embedding: {e}")
        return None

def semantic_similarity_search(query_text: str, category: Optional[str] = None, top_k: int = 4) -> List[Dict]:
    """Performs cosine similarity search using pgvector (<=> operator)."""
    try:
        vector = embeddings.embed_query(query_text)
        vector_str = format_vector(vector)

        if category:
            sql = """
                SELECT id, category, content,
                       (1 - (embedding <=> %s::vector)) AS similarity
                FROM resume_vectors
                WHERE category = %s
                ORDER BY embedding <=> %s::vector ASC
                LIMIT %s;
            """
            rows = query(sql, [vector_str, category, vector_str, top_k], fetch_all=True)
        else:
            sql = """
                SELECT id, category, content,
                       (1 - (embedding <=> %s::vector)) AS similarity
                FROM resume_vectors
                ORDER BY embedding <=> %s::vector ASC
                LIMIT %s;
            """
            rows = query(sql, [vector_str, vector_str, top_k], fetch_all=True)

        return [dict(r) for r in (rows or [])]
    except Exception as e:
        print(f"[VectorStore] Warning: Semantic search error: {e}")
        return []

def seed_default_knowledge():
    """Seeds default high-impact bullet exemplars if the vector DB table is empty."""
    try:
        count_row = query("SELECT COUNT(*) AS cnt FROM resume_vectors WHERE category = 'exemplar_bullet'", fetch_one=True)
        if count_row and count_row["cnt"] == 0:
            print("[VectorStore] Seeding default high-impact bullet exemplars into PostgreSQL pgvector...")
            for bullet in DEFAULT_EXEMPLAR_BULLETS:
                store_embedding(bullet, category="exemplar_bullet")
            print("[VectorStore] Successfully seeded exemplar vectors.")
    except Exception as e:
        print(f"[VectorStore] Could not auto-seed exemplars (PostgreSQL may be initializing): {e}")

