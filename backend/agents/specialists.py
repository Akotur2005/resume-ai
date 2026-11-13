from typing import List, Any
from pydantic import BaseModel, Field  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from chains.model import llm  # type: ignore

# ==============================================================================
# Agent 1: ATS Compliance Specialist (Layout, Parser Compatibility, Headings)
# ==============================================================================
class ComplianceReport(BaseModel):
    formatting_score: int = Field(ge=0, le=100, description="Score evaluating single column, clean typography, parseability")
    sections_score: int = Field(ge=0, le=100, description="Score evaluating presence of standard ATS headings")
    readability_score: int = Field(ge=0, le=100, description="Score evaluating bullet brevity, sentence structure, lack of clutter")
    structural_issues: List[str] = Field(default_factory=list, description="Specific structural flaws or missing standard headings")

compliance_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert ATS Compliance & Parser Auditor Agent.
Your sole mission is to audit the mechanical parseability and formatting of this resume:
1. Verify presence of standard headings: Summary, Experience, Education, Skills, Projects, Certifications.
2. Check for single-column text flow, reverse-chronological order, and consistent date formatting (e.g. Month Year - Month Year).
3. Identify unparseable artifacts: tables, multi-column setups, icons, missing contact information.
Be honest and rigorous in your evaluation."""
    ),
    (
        "human",
        "Resume Text:\n\"\"\"\n{resume}\n\"\"\"\n\nHeading Check Tool Data:\n{heading_tool_data}"
    )
])

compliance_agent: Any = compliance_prompt | llm.with_structured_output(ComplianceReport)


# ==============================================================================
# Agent 2: Semantic Keyword & Skill Strategist (PostgreSQL Vector Assisted)
# ==============================================================================
class KeywordReport(BaseModel):
    keyword_score: int = Field(ge=0, le=100, description="Overall keyword alignment score")
    matched_keywords: List[str] = Field(default_factory=list, description="Core skills and tools found in both resume and JD")
    missing_keywords: List[str] = Field(default_factory=list, description="Critical skills in JD missing from resume")

keyword_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Technical Talent Sourcer & Semantic Keyword Specialist Agent.
Your mission is to perform deep semantic alignment between the Resume and Job Description:
1. Identify matched technical skills, methodologies, frameworks, and domain concepts.
2. Identify high-priority missing keywords that an ATS scanner would filter for.
3. Leverage the PostgreSQL pgvector semantic context provided to recognize synonyms (e.g. GCP = Google Cloud Platform, FastAPI = REST APIs).
If no Job Description is provided, evaluate against industry expectations for the apparent role and suggest standard missing skills."""
    ),
    (
        "human",
        "RESUME:\n\"\"\"\n{resume}\n\"\"\"\n\nJOB DESCRIPTION:\n\"\"\"\n{job_description}\n\"\"\"\n\nPOSTGRESQL PGVECTOR SEMANTIC INSIGHTS:\n{vector_insights}"
    )
])

keyword_agent: Any = keyword_prompt | llm.with_structured_output(KeywordReport)


# ==============================================================================
# Agent 3: Executive Recruiter & Impact Coach (XYZ Formula & Metrics Audit)
# ==============================================================================
class RecruiterReport(BaseModel):
    impact_score: int = Field(ge=0, le=100, description="Score based on quantified achievements and strong action verbs")
    strengths: List[str] = Field(default_factory=list, description="Top 3 standout accomplishments or qualities")
    weak_bullets: List[str] = Field(default_factory=list, description="Up to 5 weak bullets that lack metrics or use passive verbs")
    critique_notes: List[str] = Field(default_factory=list, description="Recruiter feedback on seniority, leadership, and impact")

recruiter_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an Executive Technical Recruiter and Career Coach Agent.
Your mission is to audit candidate accomplishments using the Google XYZ Formula:
'Accomplished [X] as measured by [Y], by doing [Z]'
1. Check each bullet point for strong action verbs (e.g. Engineered, Spearheaded, Accelerated vs helped, worked on).
2. Look for quantifiable business outcomes: revenue, latency, user growth, dollar savings, or percentages.
3. Flag the 3-5 weakest bullets in the resume that need immediate rewriting."""
    ),
    (
        "human",
        "RESUME:\n\"\"\"\n{resume}\n\"\"\"\n\nMETRICS & VERBS AUDIT TOOL DATA:\n{metrics_tool_data}"
    )
])

recruiter_agent: Any = recruiter_prompt | llm.with_structured_output(RecruiterReport)


# ==============================================================================
# Agent 4: RAG-Powered Resume Rewriter & Optimizer (Vector Exemplars)
# ==============================================================================
class RewrittenItem(BaseModel):
    original: str
    improved: str

class OptimizerReport(BaseModel):
    rewritten_bullets: List[RewrittenItem] = Field(default_factory=list, description="Rewritten bullets in high-impact format")

optimizer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an Elite Executive Resume Rewriter Agent.
Your mission is to rewrite weak resume bullets into top-tier, high-impact statements:
1. Model your rewrites after the high-impact exemplars retrieved from the PostgreSQL Vector Database.
2. Enforce the standard: Strong Action Verb + Scope/Technology + Quantifiable Outcome ([X%], latency, costs, scale).
3. Naturally incorporate missing keywords identified by the Keyword Agent where relevant.
4. Keep each bullet under 25 words. Never invent false facts—use [X%] placeholders if exact metrics were not stated."""
    ),
    (
        "human",
        "WEAK BULLETS TO REWRITE:\n{weak_bullets}\n\nTARGET MISSING KEYWORDS:\n{missing_keywords}\n\nHIGH-IMPACT EXEMPLARS FROM POSTGRESQL PGVECTOR (RAG):\n{exemplars}"
    )
])

optimizer_agent: Any = optimizer_prompt | llm.with_structured_output(OptimizerReport)

