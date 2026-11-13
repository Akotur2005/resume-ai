import re
from typing import List, Dict, Any, Optional
from chains.review_chain import ReviewSchema, Breakdown, Issue, RewrittenBullet  # type: ignore
from .specialists import compliance_agent, keyword_agent, recruiter_agent, optimizer_agent
from .tools import (
    audit_ats_headings, 
    audit_action_verbs_and_metrics, 
    vector_search_skills, 
    fetch_high_impact_exemplars
)
from db.vector_store import store_embedding, seed_default_knowledge

class MultiAgentResumeOrchestrator:
    """
    Multi-Agent Orchestrator powered by pure LangChain and PostgreSQL pgvector.
    Coordinates specialized agents (ATS Compliance, Keyword Strategist, Recruiter, Optimizer)
    and executes reflection and validation loops.
    """

    def __init__(self):
        # Auto-seed pgvector exemplars if needed
        try:
            seed_default_knowledge()
        except Exception:
            pass

    def extract_bullets_from_text(self, text: str) -> List[str]:
        """Extracts bullet lines or action statements from raw resume text."""
        lines = text.split("\n")
        bullets = []
        for line in lines:
            cleaned = line.strip()
            # Match standard bullet characters or leading dash/bullet
            if cleaned.startswith(("-", "*", "•", "–", "—", ">")):
                bullets.append(cleaned.lstrip("-*•–—> ").strip())
            elif len(cleaned) > 25 and len(cleaned) < 250 and cleaned[0].isupper() and cleaned.endswith("."):
                bullets.append(cleaned)
        return bullets[:15] if bullets else [l.strip() for l in lines if len(l.strip()) > 30][:10]

    def analyze(self, resume_text: str, job_description: str = "", resume_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Coordinates the complete Multi-Agent analysis pipeline:
        1. Tool Execution (Regex audits + pgvector semantic retrieval)
        2. Specialized Agent Invocations
        3. RAG Retrieval from PostgreSQL pgvector
        4. Optimization & Bullet Rewriting
        5. Reflection & Quality Gate
        6. Vector Database Indexing
        """
        # Step 1: Tool Executions
        heading_tool_data: Any = audit_ats_headings.invoke(resume_text)
        candidate_bullets: List[str] = self.extract_bullets_from_text(resume_text)
        metrics_tool_data: Any = audit_action_verbs_and_metrics.invoke(candidate_bullets)
        vector_insights: Any = vector_search_skills.invoke(job_description or "")

        # Step 2: Specialized Agent 1 - ATS Compliance Agent
        comp_report: Any = compliance_agent.invoke({
            "resume": resume_text,
            "heading_tool_data": str(heading_tool_data)
        })

        # Step 3: Specialized Agent 2 - Semantic Keyword Strategist
        kw_report: Any = keyword_agent.invoke({
            "resume": resume_text,
            "job_description": job_description or "(none provided)",
            "vector_insights": str(vector_insights)
        })

        # Step 4: Specialized Agent 3 - Executive Recruiter & Impact Coach
        rec_report: Any = recruiter_agent.invoke({
            "resume": resume_text,
            "metrics_tool_data": str(metrics_tool_data)
        })

        # Step 5: RAG Lookup in PostgreSQL pgvector for high-impact exemplars
        weak_bullets = rec_report.weak_bullets[:5]
        if not weak_bullets and candidate_bullets:
            weak_bullets = candidate_bullets[:3]
        if not weak_bullets:
            weak_bullets = ["Managed day-to-day software development and assisted team with application deployment."]

        exemplars: Any = fetch_high_impact_exemplars.invoke("\n".join(weak_bullets))

        # Step 6: Specialized Agent 4 - Resume Optimizer (Rewriter)
        opt_report: Any = optimizer_agent.invoke({
            "weak_bullets": "\n".join(weak_bullets),
            "missing_keywords": ", ".join(kw_report.missing_keywords[:6]),
            "exemplars": exemplars
        })

        # Step 7: Reflection & Validation Loop (Agent Self-Correction)
        verified_bullets: List[RewrittenBullet] = []
        metric_pattern = re.compile(r"(\d+[\.,]?\d*[%kMB]?|\$[\d,]+|\b\d+\b|\[X%\])")

        for item in opt_report.rewritten_bullets:
            orig = item.original.strip()
            rev = item.improved.strip()

            # Reflection check: does the rewrite contain a measurable outcome?
            if not metric_pattern.search(rev):
                rev = f"{rev.rstrip('.')} resulting in a [X%] improvement in system performance."

            verified_bullets.append(RewrittenBullet(original=orig, improved=rev))

        # Step 8: Calculate Weighted Overall ATS Score
        overall_score = int(
            (comp_report.formatting_score * 0.20) +
            (comp_report.sections_score * 0.15) +
            (kw_report.keyword_score * 0.30) +
            (rec_report.impact_score * 0.25) +
            (comp_report.readability_score * 0.10)
        )
        overall_score = max(0, min(100, overall_score))

        # Step 9: Synthesize Prioritized Issues
        issues: List[Issue] = []
        for flaw in comp_report.structural_issues:
            issues.append(Issue(
                severity="high",
                section="Formatting & Structure",
                problem=flaw,
                fix="Use standard single-column flow with recognized section titles (Summary, Experience, Education, Skills, Projects)."
            ))

        for flaw in rec_report.critique_notes:
            issues.append(Issue(
                severity="medium",
                section="Experience & Impact",
                problem=flaw,
                fix="Adopt the Google XYZ formula: Action Verb + Project Context + Measurable Outcome ([X%])."
            ))

        if kw_report.missing_keywords:
            issues.append(Issue(
                severity="medium",
                section="Keywords",
                problem=f"Missing high-demand skills: {', '.join(kw_report.missing_keywords[:4])}",
                fix="Naturally integrate these keywords into your Skills section and relevant project bullet points."
            ))

        # Step 10: Index resume chunks into PostgreSQL pgvector for semantic retrieval
        try:
            # Store primary resume chunk in pgvector
            chunk = resume_text[:2000].strip()
            store_embedding(chunk, category="resume_chunk", resume_id=resume_id)
        except Exception as e:
            print(f"[Orchestrator] Note: Non-critical vector storage notice: {e}")

        # Step 11: Compile final ReviewSchema response
        primary_strength = rec_report.strengths[0] if rec_report.strengths else "solid foundational qualifications"
        summary_text = (
            f"Comprehensive audit conducted by 4 specialized LangChain agents with PostgreSQL pgvector. "
            f"Candidate displays {primary_strength}. "
            f"Key recommendations focus on increasing quantifiable metric density and aligning with missing role keywords."
        )

        final_review = ReviewSchema(
            atsScore=overall_score,
            breakdown=Breakdown(
                formatting=comp_report.formatting_score,
                keywords=kw_report.keyword_score,
                sections=comp_report.sections_score,
                impact=rec_report.impact_score,
                readability=comp_report.readability_score
            ),
            summary=summary_text,
            strengths=rec_report.strengths or ["Clear chronological progression", "Relevant domain background"],
            issues=issues,
            matchedKeywords=kw_report.matched_keywords,
            missingKeywords=kw_report.missing_keywords,
            rewrittenBullets=verified_bullets
        )

        return final_review.model_dump()

