from typing import List, Optional, Any
from pydantic import BaseModel, Field  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from chains.model import llm  # type: ignore
from chains.builder_chain import ExperienceItem, EducationItem, ProjectItem, ResumeSchema  # type: ignore

# ==============================================================================
# Agent 1: JD Requirements & Skill Extraction Agent
# ==============================================================================
class JdSkillAnalysis(BaseModel):
    target_role: str = Field(description="Normalized target job title")
    seniority_level: str = Field(description="e.g. Junior, Mid, Senior, Lead, Staff, Principal, Executive")
    primary_skills: List[str] = Field(description="Must-have core technologies and languages")
    tools_and_frameworks: List[str] = Field(description="Supporting frameworks, libraries, cloud tools, databases")
    domain_keywords: List[str] = Field(description="Methodologies, industry buzzwords, standards (e.g. CI/CD, Agile, Microservices)")

jd_analyzer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an elite Technical Talent Sourcer & Job Requirements Specialist Agent.
Analyze the target Job Description to extract essential requirements for building an ATS-winning resume.
Identify:
1. Target role and seniority level.
2. Primary core skills (hard tech requirements).
3. Secondary frameworks, databases, and cloud tools.
4. Domain methodologies and high-priority keywords that ATS algorithms filter for.
Incorporate the PostgreSQL pgvector semantic context provided to identify related technologies."""
    ),
    (
        "human",
        "JOB DESCRIPTION:\n\"\"\"\n{job_description}\n\"\"\"\n\nUSER SPECIFIED TITLE:\n{target_title}\n\nPOSTGRESQL PGVECTOR SEMANTIC INSIGHTS:\n{vector_insights}"
    )
])

jd_analyzer_agent: Any = jd_analyzer_prompt | llm.with_structured_output(JdSkillAnalysis)


# ==============================================================================
# Agent 2: Experience & Accomplishment Architect Agent (XYZ Formula + RAG)
# ==============================================================================
class ExperienceGeneration(BaseModel):
    experience: List[ExperienceItem] = Field(description="List of chronological, high-impact job positions")

experience_architect_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an Executive Career Coach & Accomplishment Architect Agent.
Your mission is to construct realistic, highly competitive employment history items tailored for the target role:
- PAGE LENGTH REQUIREMENT: {target_pages} page(s).
  * If TARGET PAGES is 1: Generate 2 to 3 chronological job roles with 3-4 accomplishment bullets each.
  * If TARGET PAGES is 2 (or more): Generate 4 to 5 chronological job roles spanning past career progression with 4-5 high-impact accomplishment bullets each.
- Strictly follow Google's XYZ Formula for all bullets:
  'Accomplished [X] as measured by [Y], by doing [Z]'
- Model your bullets on the high-impact exemplars retrieved from the PostgreSQL pgvector database.
- Incorporate the target skills and tools naturally.
- Max 25 words per bullet. If no real numbers are given in candidate notes, use [X%] placeholders."""
    ),
    (
        "human",
        """TARGET ROLE: {target_role} ({seniority_level})
PAGE LENGTH: {target_pages} page(s)
REQUIRED TECH STACK: {skills}
DOMAIN KEYWORDS: {keywords}
CANDIDATE NOTES / BACKGROUND: {user_notes}

HIGH-IMPACT EXEMPLARS FROM POSTGRESQL PGVECTOR (RAG):
{exemplars}"""
    )
])

experience_architect_agent: Any = experience_architect_prompt | llm.with_structured_output(ExperienceGeneration)


# ==============================================================================
# Agent 3: Technical Project Specialist Agent
# ==============================================================================
class ProjectsGeneration(BaseModel):
    projects: List[ProjectItem] = Field(description="Technical showcase projects")

project_specialist_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Technical Project & Portfolio Architect Agent.
Generate technical showcase projects matching the target role and page length:
- If TARGET PAGES is 1: Generate 2 focused technical showcase projects.
- If TARGET PAGES is 2 (or more): Generate 3 to 4 in-depth technical projects highlighting end-to-end architecture, scale, and technical depth.
Choose realistic, modern project concepts (e.g. Distributed system, AI pipeline, microservices, cloud infra).
Explicitly list the tech stack (e.g. Python, Docker, PostgreSQL, React).
Provide 2-3 bullet points per project demonstrating architecture, scalability, and measurable results ([X%])."""
    ),
    (
        "human",
        "TARGET ROLE: {target_role}\nPAGE LENGTH: {target_pages} page(s)\nPRIMARY TECH: {skills}\nFRAMEWORKS & TOOLS: {tools}"
    )
])

project_specialist_agent: Any = project_specialist_prompt | llm.with_structured_output(ProjectsGeneration)


# ==============================================================================
# Agent 4: Summary & Credentials Strategist Agent
# ==============================================================================
class SummaryAndEducation(BaseModel):
    summary: str = Field(description="Impactful ATS summary in first-person-implied style")
    education: List[EducationItem] = Field(description="Standard education entries")
    certifications: List[str] = Field(description="Standard high-value industry certifications for this role")

summary_education_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an Executive Resume Strategist Agent.
Draft an elite ATS-optimized Professional Summary and recommend standard education & certifications:
1. Professional Summary: Impactful sentences in first-person-implied style (strictly no 'I' or 'my'). Include years of experience, core tech stack, and major achievements.
   - If TARGET PAGES is 2, make it a 4-5 sentence comprehensive executive summary emphasizing leadership, technical architecture, and business ROI.
2. Education: Recommend appropriate Degree, Major, and university placeholder.
3. Certifications: If TARGET PAGES is 1, include 2 standard certifications. If TARGET PAGES is 2, include 3 to 4 high-value industry-recognized certifications (e.g. AWS Certified Solutions Architect, CKA, Google Cloud, PMP)."""
    ),
    (
        "human",
        "TARGET ROLE: {target_role}\nSENIORITY: {seniority}\nPAGE LENGTH: {target_pages} page(s)\nKEY SKILLS: {skills}\nEXPERIENCE SUMMARY: {exp_summary}\nCANDIDATE NOTES: {user_notes}"
    )
])

summary_education_agent: Any = summary_education_prompt | llm.with_structured_output(SummaryAndEducation)


# ==============================================================================
# Agent 5: ATS Quality Control & Reflection Agent (Quality Gate)
# ==============================================================================
class BulletReflectionItem(BaseModel):
    original: str
    improved: str

class QualityAuditReport(BaseModel):
    missing_critical_skills: List[str] = Field(description="Any critical skills missing from the generated content")
    bullets_improved: List[BulletReflectionItem] = Field(description="Refined bullets that needed stronger metrics or action verbs")

ats_critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an ATS Quality Assurance & Reflection Agent.
Inspect the assembled resume draft against strict ATS standards:
1. Verify that all bullets start with a strong action verb (Spearheaded, Architected, Engineered, Accelerated).
2. Ensure every bullet contains a quantifiable metric or [X%] placeholder.
3. If any bullet is passive or lacks a metric, rewrite it into a high-impact achievement under 25 words."""
    ),
    (
        "human",
        "DRAFT BULLETS:\n{bullets}\n\nREQUIRED SKILLS:\n{skills}"
    )
])

ats_critic_agent: Any = ats_critic_prompt | llm.with_structured_output(QualityAuditReport)
