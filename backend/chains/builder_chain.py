import re
from typing import List, Optional
from pydantic import BaseModel, Field  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from langchain_core.output_parsers import StrOutputParser  # type: ignore
try:
    from chains.model import llm  # type: ignore
except ImportError:
    from .model import llm  # type: ignore

# ---- Structured resume schema for parser and generator ----
class ExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    start: str = ""
    end: str = ""
    bullets: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    start: str = ""
    end: str = ""
    grade: str = ""

class ProjectItem(BaseModel):
    name: str = ""
    tech: str = ""
    bullets: List[str] = Field(default_factory=list)

class ResumeSchema(BaseModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: List[str] = Field(default_factory=list)
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


# ---- Fallback prompts for basic chains ----
bullet_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You rewrite resume bullets for ATS. Output ONE bullet only, no quotes, no dash.
Format: strong action verb + what you did + tool/tech + measurable result.
Max 25 words. Do not invent numbers: if none are given, use a placeholder like [X%].""",
    ),
    (
        "human",
        "Role: {role}\nTarget job: {targetRole}\nRaw bullet: {bullet}",
    ),
])

summary_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Write a 3-sentence ATS-friendly professional summary in first-person-implied style
(no "I"). Include years of experience, core skills, and one achievement.
Plain text only. Use keywords from the target role.""",
    ),
    (
        "human",
        "Target role: {targetRole}\nSkills: {skills}\nExperience:\n{experience}",
    ),
])

parse_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Extract the resume text into the schema. Use empty strings/arrays for missing data. Never invent facts.",
    ),
    ("human", "{text}"),
])

parse_chain = parse_prompt | llm.with_structured_output(ResumeSchema)

generate_from_jd_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an elite ATS resume builder and career strategist.
Craft a complete, top-tier, 100% ATS-optimized resume tailored directly to the provided Job Description.""",
    ),
    (
        "human",
        "JOB DESCRIPTION:\n{jobDescription}\n\nCANDIDATE NOTES / BACKGROUND:\n{userNotes}\n\nCANDIDATE NAME:\n{fullName}\n\nTARGET JOB TITLE:\n{targetTitle}",
    ),
])

# ---- Multi-Agent Coordinators ----
_builder = None

def get_builder():
    global _builder
    if _builder is None:
        from agents.builder_coordinator import MultiAgentResumeBuilder
        _builder = MultiAgentResumeBuilder()
    return _builder

class MultiAgentBulletChain:
    """Multi-Agent Bullet Optimizer using pgvector RAG exemplars and reflection verification."""
    def invoke(self, inputs: dict) -> str:
        try:
            builder: Any = get_builder()
            return str(builder.improve_bullet(
                bullet=inputs.get("bullet", ""),
                role=inputs.get("role", ""),
                target_role=inputs.get("targetRole", "")
            ))
        except Exception as e:
            print(f"[BulletChain] Multi-Agent notice ({e}), running fallback chain...")
            return str((bullet_prompt | llm | StrOutputParser()).invoke(inputs))

class MultiAgentSummaryChain:
    """Multi-Agent Professional Summary Generator with keyword targeting."""
    def invoke(self, inputs: dict) -> str:
        try:
            builder: Any = get_builder()
            skills_input = inputs.get("skills", "")
            if isinstance(skills_input, str):
                skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
            else:
                skills_list = list(skills_input or [])
            return str(builder.generate_summary(
                target_role=inputs.get("targetRole", ""),
                skills=skills_list,
                experience=inputs.get("experience", "")
            ))
        except Exception as e:
            print(f"[SummaryChain] Multi-Agent notice ({e}), running fallback chain...")
            return str((summary_prompt | llm | StrOutputParser()).invoke(inputs))

class MultiAgentGenerateFromJdChain:
    """Multi-Agent Resume Construction Engine (JD Skills + Experience Architect + Projects + ATS QA)."""
    def invoke(self, inputs: dict):
        try:
            builder: Any = get_builder()
            return builder.generate_from_jd(
                job_description=inputs.get("jobDescription", ""),
                user_notes=inputs.get("userNotes", ""),
                full_name=inputs.get("fullName", "Your Name"),
                target_title=inputs.get("targetTitle", ""),
                page_count=inputs.get("pageCount", 1)
            )
        except Exception as e:
            print(f"[GenerateFromJd] Multi-Agent notice ({e}), running fallback chain...")
            return (generate_from_jd_prompt | llm.with_structured_output(ResumeSchema)).invoke(inputs)

# Exported chains hooked to the Multi-Agent system
bullet_chain = MultiAgentBulletChain()
summary_chain = MultiAgentSummaryChain()
generate_from_jd_chain = MultiAgentGenerateFromJdChain()
