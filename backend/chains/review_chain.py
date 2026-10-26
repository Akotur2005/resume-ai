from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from .model import llm

class Breakdown(BaseModel):
    formatting: int = Field(ge=0, le=100)
    keywords: int = Field(ge=0, le=100)
    sections: int = Field(ge=0, le=100)
    impact: int = Field(ge=0, le=100, description="Quantified achievements, action verbs")
    readability: int = Field(ge=0, le=100)

class Issue(BaseModel):
    severity: Literal["high", "medium", "low"]
    section: str
    problem: str
    fix: str

class RewrittenBullet(BaseModel):
    original: str
    improved: str

class ReviewSchema(BaseModel):
    atsScore: int = Field(ge=0, le=100, description="Overall ATS score 0-100")
    breakdown: Breakdown
    summary: str = Field(description="2-3 sentence overall verdict")
    strengths: List[str]
    issues: List[Issue]
    matchedKeywords: List[str]
    missingKeywords: List[str] = Field(description="Keywords from the job description absent in resume")
    rewrittenBullets: List[RewrittenBullet] = Field(description="Up to 5 weak bullets rewritten with action verb + metric")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert ATS (Applicant Tracking System) analyst and technical recruiter.
Score the resume honestly. Rules for ATS-friendliness:
- Single column, no tables, no images, no text boxes, no icons
- Standard headings: Summary, Experience, Education, Skills, Projects, Certifications
- Consistent dates (MMM YYYY), reverse-chronological order
- Bullets start with strong action verbs and include metrics where possible
- Keywords should mirror the job description when one is provided
If no job description is given, evaluate for general ATS-readiness and set missingKeywords to common keywords for the apparent role.
Never invent experience. Only judge what is in the resume text.""",
    ),
    (
        "human",
        """RESUME TEXT:
\"\"\"
{resume}
\"\"\"

JOB DESCRIPTION (may be empty):
\"\"\"
{jobDescription}
\"\"\"""",
    ),
])

# LangChain LCEL pipeline with structured Pydantic output
review_chain = prompt | llm.with_structured_output(ReviewSchema)

def review_resume(resume: str, job_description: str = "") -> dict:
    result = review_chain.invoke({
        "resume": resume,
        "jobDescription": job_description or "(none provided)"
    })
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if isinstance(result, dict):
        return result
    return result.dict()
