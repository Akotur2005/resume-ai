import re
from typing import List, Dict, Any
from langchain_core.tools import tool  # type: ignore
from db.vector_store import semantic_similarity_search

STANDARD_HEADINGS = ["summary", "experience", "education", "skills", "projects", "certifications"]

WEAK_VERBS = [
    "worked on", "responsible for", "helped", "assisted", 
    "handled", "participated in", "did", "tasked with", "involved in"
]

STRONG_VERBS = [
    "spearheaded", "engineered", "architected", "accelerated", 
    "optimized", "deployed", "scaled", "automated", "mentored",
    "designed", "developed", "executed", "formulated", "transformed"
]

@tool
def audit_ats_headings(resume_text: str) -> Dict[str, Any]:
    """Scans resume text for standard ATS-compliant section headings."""
    found_headings = []
    missing_headings = []
    lower_text = resume_text.lower()

    for h in STANDARD_HEADINGS:
        if re.search(rf"\b{h}\b", lower_text):
            found_headings.append(h.capitalize())
        else:
            missing_headings.append(h.capitalize())

    return {
        "found": found_headings,
        "missing": missing_headings,
        "is_complete": len(missing_headings) <= 1
    }

@tool
def audit_action_verbs_and_metrics(bullets: List[str]) -> Dict[str, Any]:
    """Inspects resume bullet points for measurable metrics (%, $, numbers) and flags weak action verbs."""
    metric_pattern = re.compile(r"(\d+[\.,]?\d*[%kMB]?|\$[\d,]+|\b\d+\b)")
    weak_bullets = []
    strong_bullets = []

    for b in bullets:
        b_clean = b.strip()
        if not b_clean:
            continue
        has_metric = bool(metric_pattern.search(b_clean))
        has_weak_verb = any(wv in b_clean.lower() for wv in WEAK_VERBS)

        if not has_metric or has_weak_verb:
            weak_bullets.append(b_clean)
        else:
            strong_bullets.append(b_clean)

    return {
        "strong_count": len(strong_bullets),
        "weak_bullets": weak_bullets[:5]
    }

@tool
def vector_search_skills(job_description: str) -> str:
    """Queries PostgreSQL pgvector to retrieve semantically related skills and domain competencies."""
    if not job_description or len(job_description.strip()) < 20:
        return "No job description provided for vector search."

    matches = semantic_similarity_search(job_description, category="skill", top_k=5)
    if not matches:
        return "Standard domain competencies will be extracted via direct semantic analysis."

    return "\n".join([f"- {m['content']} (similarity: {round(m['similarity'], 2)})" for m in matches])

@tool
def fetch_high_impact_exemplars(bullet_context: str) -> str:
    """Queries PostgreSQL pgvector for high-impact exemplar bullet points matching the role or task."""
    matches = semantic_similarity_search(bullet_context, category="exemplar_bullet", top_k=3)
    if not matches:
        return "Recruiter Standard: Action Verb + Responsibility/Task + Tech Stack + Measurable Outcome ([X%])."

    return "\n".join([f"- Exemplar: {m['content']}" for m in matches])

