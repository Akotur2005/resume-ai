import { ChatPromptTemplate } from "@langchain/core/prompts";
import { z } from "zod";
import { llm } from "./model.js";

// 1) The SHAPE of the answer we want. LangChain forces the model to return exactly this.
export const reviewSchema = z.object({
  atsScore: z.number().int().min(0).max(100).describe("Overall ATS score 0-100"),
  breakdown: z.object({
    formatting: z.number().int().min(0).max(100),
    keywords: z.number().int().min(0).max(100),
    sections: z.number().int().min(0).max(100),
    impact: z.number().int().min(0).max(100).describe("Quantified achievements, action verbs"),
    readability: z.number().int().min(0).max(100),
  }),
  summary: z.string().describe("2-3 sentence overall verdict"),
  strengths: z.array(z.string()),
  issues: z.array(
    z.object({
      severity: z.enum(["high", "medium", "low"]),
      section: z.string(),
      problem: z.string(),
      fix: z.string(),
    })
  ),
  matchedKeywords: z.array(z.string()),
  missingKeywords: z.array(z.string()).describe("Keywords from the job description absent in resume"),
  rewrittenBullets: z.array(
    z.object({ original: z.string(), improved: z.string() })
  ).describe("Up to 5 weak bullets rewritten with action verb + metric"),
});

// 2) The PROMPT template with {variables}.
const prompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `You are an expert ATS (Applicant Tracking System) analyst and technical recruiter.
Score the resume honestly. Rules for ATS-friendliness:
- Single column, no tables, no images, no text boxes, no icons
- Standard headings: Summary, Experience, Education, Skills, Projects, Certifications
- Consistent dates (MMM YYYY), reverse-chronological order
- Bullets start with strong action verbs and include metrics where possible
- Keywords should mirror the job description when one is provided
If no job description is given, evaluate for general ATS-readiness and set missingKeywords to common keywords for the apparent role.
Never invent experience. Only judge what is in the resume text.`,
  ],
  [
    "human",
    `RESUME TEXT:
"""
{resume}
"""

JOB DESCRIPTION (may be empty):
"""
{jobDescription}
"""`,
  ],
]);

// 3) The CHAIN: prompt -> model (structured output). "|" is LangChain's pipe (LCEL).
export const reviewChain = prompt.pipe(llm.withStructuredOutput(reviewSchema, { name: "resume_review" }));

export async function reviewResume(resume, jobDescription = "") {
  return reviewChain.invoke({ resume, jobDescription: jobDescription || "(none provided)" });
}
