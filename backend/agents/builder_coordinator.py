import re
from typing import Dict, Any, List
from chains.builder_chain import ResumeSchema, ExperienceItem, ProjectItem, EducationItem  # type: ignore
from .builder_agents import (
    jd_analyzer_agent,
    experience_architect_agent,
    project_specialist_agent,
    summary_education_agent,
    ats_critic_agent
)
from .tools import vector_search_skills, fetch_high_impact_exemplars
from chains.model import llm  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from langchain_core.output_parsers import StrOutputParser  # type: ignore

class MultiAgentResumeBuilder:
    """
    Multi-Agent Resume Construction & Optimization Engine.
    Orchestrates specialized builder agents:
    - JD Skills Analyzer (Vector RAG)
    - Experience Architect (XYZ formula, 1-page vs 2-page scaling)
    - Project Specialist
    - Summary & Credentials Strategist
    - ATS Critic & Quality Assurance (Reflection Loop)
    """

    def generate_from_jd(
        self,
        job_description: str,
        user_notes: str = "",
        full_name: str = "Your Name",
        target_title: str = "",
        page_count: int = 1
    ) -> Dict[str, Any]:
        """
        Executes collaborative multi-agent workflow to generate a complete ATS-compliant resume from a JD.
        Supports 1-page (compact / standard) and 2-page (comprehensive / senior) generation.
        """
        page_count = max(1, min(3, int(page_count or 1)))

        # Step 1: Query pgvector for semantic skill context
        vector_insights = vector_search_skills.invoke(job_description)

        # Step 2: Agent 1 - Extract role & skills
        analysis = jd_analyzer_agent.invoke({
            "job_description": job_description,
            "target_title": target_title or "Target Role",
            "vector_insights": str(vector_insights)
        })

        effective_role = target_title or analysis.target_role
        combined_skills = analysis.primary_skills + analysis.tools_and_frameworks

        # Step 3: Query pgvector for high-impact accomplishment exemplars
        exemplars = fetch_high_impact_exemplars.invoke(f"{effective_role} {' '.join(analysis.primary_skills[:4])}")

        # Step 4: Agent 2 - Construct Experience section scaled to target pages
        exp_report = experience_architect_agent.invoke({
            "target_role": effective_role,
            "seniority_level": analysis.seniority_level,
            "target_pages": str(page_count),
            "skills": ", ".join(combined_skills),
            "keywords": ", ".join(analysis.domain_keywords),
            "user_notes": user_notes or "(none provided)",
            "exemplars": exemplars
        })

        # Step 5: Agent 3 - Generate showcase projects scaled to target pages
        proj_report = project_specialist_agent.invoke({
            "target_role": effective_role,
            "target_pages": str(page_count),
            "skills": ", ".join(analysis.primary_skills),
            "tools": ", ".join(analysis.tools_and_frameworks)
        })

        # Step 6: Agent 4 - Generate Summary, Education & Certifications
        exp_summary_snippet = "\n".join([
            f"{e.title} at {e.company}: {'; '.join(e.bullets[:2])}"
            for e in exp_report.experience
        ])

        summary_report = summary_education_agent.invoke({
            "target_role": effective_role,
            "seniority": analysis.seniority_level,
            "target_pages": str(page_count),
            "skills": ", ".join(combined_skills[:10]),
            "exp_summary": exp_summary_snippet,
            "user_notes": user_notes or ""
        })

        # Step 7: Agent 5 - Reflection & Quality Assurance Loop
        all_draft_bullets = []
        for e in exp_report.experience:
            all_draft_bullets.extend(e.bullets)

        critic_report = ats_critic_agent.invoke({
            "bullets": "\n".join(all_draft_bullets[:12]),
            "skills": ", ".join(analysis.primary_skills[:6])
        })

        # Apply improvements from the QA reflection agent
        replacements = {item.original.strip(): item.improved.strip() for item in critic_report.bullets_improved}
        refined_experience = []
        for e in exp_report.experience:
            refined_bullets = [replacements.get(b.strip(), b) for b in e.bullets]
            refined_experience.append(ExperienceItem(
                company=e.company,
                title=e.title,
                location=e.location or "Remote",
                start=e.start,
                end=e.end,
                bullets=refined_bullets
            ))

        # Step 8: Build unified structured resume
        resume = ResumeSchema(
            fullName=full_name or "Your Name",
            email="candidate.email@example.com",
            phone="+1 (555) 019-2834",
            location="San Francisco, CA (Open to Remote)",
            links=["linkedin.com/in/profile", "github.com/profile"],
            summary=summary_report.summary,
            skills=combined_skills,
            experience=refined_experience,
            education=summary_report.education or [
                EducationItem(
                    school="State University",
                    degree="Bachelor of Science in Computer Science",
                    start="2018",
                    end="2022",
                    grade="3.8 GPA"
                )
            ],
            projects=proj_report.projects,
            certifications=summary_report.certifications
        )

        return resume.model_dump()

    def improve_bullet(self, bullet: str, role: str = "", target_role: str = "") -> str:
        """
        Multi-Agent Bullet Point Optimizer using pgvector RAG exemplars and reflection verification.
        """
        # Retrieve exemplars from PostgreSQL pgvector
        exemplars = fetch_high_impact_exemplars.invoke(f"{target_role or role} {bullet}")

        bullet_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an elite Resume Bullet Optimization Agent.
Rewrite the candidate's raw bullet into an ATS-winning accomplishment statement:
1. Follow Google's XYZ formula: Strong Action Verb + Project/Task Scope + Technology Used + Measurable Outcome.
2. Model after the PostgreSQL pgvector exemplars provided.
3. Max 25 words. Output ONE single bullet only, no quotes, no dashes, no preamble.
4. If no metric is given, include a placeholder like [X%] or [X ms]."""
            ),
            (
                "human",
                "ROLE: {role}\nTARGET ROLE: {targetRole}\nRAW BULLET: {bullet}\n\nEXEMPLARS FROM PGVECTOR:\n{exemplars}"
            )
        ])

        chain = bullet_prompt | llm | StrOutputParser()
        draft = chain.invoke({
            "role": role or "Software Engineer",
            "targetRole": target_role or role or "Target Role",
            "bullet": bullet,
            "exemplars": exemplars
        }).strip()

        # Reflection check: Ensure metric exists
        if not re.search(r"(\d+[%kMB]?|\$[\d,]+|\[X%\])", draft):
            draft = f"{draft.rstrip('.')} resulting in a [X%] improvement in operational efficiency."

        return draft

    def generate_summary(self, target_role: str, skills: List[str], experience: str) -> str:
        """
        Multi-Agent Professional Summary Generator with keyword targeting.
        """
        summary_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an Executive Career Strategist Agent.
Write a powerful 3-4 sentence ATS-friendly professional summary in first-person-implied style (strictly no 'I', 'me', or 'my'):
1. Sentence 1: Professional identity, target title, and years of specialized experience.
2. Sentence 2: Core competencies, technical toolkit, and domain mastery.
3. Sentence 3: Standout quantifiable career accomplishment.
Plain text only. Maximize keyword alignment with the target role."""
            ),
            (
                "human",
                "Target Role: {targetRole}\nSkills: {skills}\nExperience Summary:\n{experience}"
            )
        ])

        chain = summary_prompt | llm | StrOutputParser()
        return chain.invoke({
            "targetRole": target_role or "Technical Specialist",
            "skills": ", ".join(skills),
            "experience": experience
        }).strip()
