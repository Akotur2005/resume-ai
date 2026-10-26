from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .model import llm

# ---- Chain A: improve a single experience/project bullet ----
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

bullet_chain = bullet_prompt | llm | StrOutputParser()


# ---- Chain B: generate a professional summary from structured resume data ----
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

summary_chain = summary_prompt | llm | StrOutputParser()


# ---- Chain C & D: Structured resume schema for parser and generator ----
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
Your mission is to craft a complete, top-tier, 100% ATS-optimized resume tailored directly to the provided Job Description.

ATS Guidelines to strictly follow:
1. Contact Info: Use the candidate name if provided; otherwise use "Your Name". Provide clean placeholder contact info if not provided.
2. Professional Summary: 3-4 concise, impactful sentences in first-person-implied style packed with exact keywords, relevant technologies, and core competencies required by the job.
3. Skills: Group or list all high-priority hard skills, frameworks, databases, cloud tools, and key methodologies explicitly requested in the JD.
4. Experience: Generate 2-3 realistic, high-impact job positions directly relevant to the role. For each position, provide 3-4 bullet points starting with strong action verbs (e.g. Engineered, Architected, Spearheaded, Accelerated), embedding relevant technologies and quantifiable outcomes ([X%], latency reduction, cost savings, user scale).
5. Projects: Include 2 realistic, technically impressive projects that showcase the demanded tech stack.
6. Education & Certifications: Include appropriate degree, major, and standard industry certifications looked for by ATS scanners.
7. Candidate Context: If the candidate provided any notes, past experience, or skills, align and incorporate their background to best match the JD without fabricating impossible credentials. If no personal notes are provided, generate a competitive profile tailored for the role.""",
    ),
    (
        "human",
        "JOB DESCRIPTION:\n{jobDescription}\n\nCANDIDATE NOTES / BACKGROUND (optional):\n{userNotes}\n\nCANDIDATE NAME (optional):\n{fullName}\n\nTARGET JOB TITLE (optional):\n{targetTitle}",
    ),
])

generate_from_jd_chain = generate_from_jd_prompt | llm.with_structured_output(ResumeSchema)
