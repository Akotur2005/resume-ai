import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { z } from "zod";
import { llm } from "./model.js";

// ---- Chain A: improve a single experience/project bullet --------------------
const bulletPrompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `You rewrite resume bullets for ATS. Output ONE bullet only, no quotes, no dash.
Format: strong action verb + what you did + tool/tech + measurable result.
Max 25 words. Do not invent numbers: if none are given, use a placeholder like [X%].`,
  ],
  ["human", "Role: {role}\nTarget job: {targetRole}\nRaw bullet: {bullet}"],
]);

export const bulletChain = bulletPrompt.pipe(llm).pipe(new StringOutputParser());

// ---- Chain B: generate a professional summary from structured resume data ---
const summaryPrompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `Write a 3-sentence ATS-friendly professional summary in first-person-implied style
(no "I"). Include years of experience, core skills, and one achievement.
Plain text only. Use keywords from the target role.`,
  ],
  ["human", "Target role: {targetRole}\nSkills: {skills}\nExperience:\n{experience}"],
]);

export const summaryChain = summaryPrompt.pipe(llm).pipe(new StringOutputParser());

// ---- Chain C: turn messy free text into the structured resume JSON ----------
export const resumeSchema = z.object({
  fullName: z.string(),
  email: z.string(),
  phone: z.string(),
  location: z.string(),
  links: z.array(z.string()),
  summary: z.string(),
  skills: z.array(z.string()),
  experience: z.array(
    z.object({
      company: z.string(),
      title: z.string(),
      location: z.string(),
      start: z.string(),
      end: z.string(),
      bullets: z.array(z.string()),
    })
  ),
  education: z.array(
    z.object({
      school: z.string(),
      degree: z.string(),
      start: z.string(),
      end: z.string(),
      grade: z.string(),
    })
  ),
  projects: z.array(
    z.object({ name: z.string(), tech: z.string(), bullets: z.array(z.string()) })
  ),
  certifications: z.array(z.string()),
});

const parsePrompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    "Extract the resume text into the schema. Use empty strings/arrays for missing data. Never invent facts.",
  ],
  ["human", "{text}"],
]);

export const parseChain = parsePrompt.pipe(llm.withStructuredOutput(resumeSchema, { name: "resume" }));

// ---- Chain D: generate complete ATS resume directly from Job Description ----
const generateFromJdPrompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `You are an elite ATS resume builder and career strategist.
Your mission is to craft a complete, top-tier, 100% ATS-optimized resume tailored directly to the provided Job Description.

ATS Guidelines to strictly follow:
1. Contact Info: Use the candidate name if provided; otherwise use "Your Name". Provide clean placeholder contact info if not provided.
2. Professional Summary: 3-4 concise, impactful sentences in first-person-implied style packed with exact keywords, relevant technologies, and core competencies required by the job.
3. Skills: Group or list all high-priority hard skills, frameworks, databases, cloud tools, and key methodologies explicitly requested in the JD.
4. Experience: Generate 2-3 realistic, high-impact job positions directly relevant to the role. For each position, provide 3-4 bullet points starting with strong action verbs (e.g. Engineered, Architected, Spearheaded, Accelerated), embedding relevant technologies and quantifiable outcomes ([X%], latency reduction, cost savings, user scale).
5. Projects: Include 2 realistic, technically impressive projects that showcase the demanded tech stack.
6. Education & Certifications: Include appropriate degree, major, and standard industry certifications looked for by ATS scanners.
7. Candidate Context: If the candidate provided any notes, past experience, or skills, align and incorporate their background to best match the JD without fabricating impossible credentials. If no personal notes are provided, generate a competitive profile tailored for the role.`,
  ],
  [
    "human",
    "JOB DESCRIPTION:\n{jobDescription}\n\nCANDIDATE NOTES / BACKGROUND (optional):\n{userNotes}\n\nCANDIDATE NAME (optional):\n{fullName}\n\nTARGET JOB TITLE (optional):\n{targetTitle}",
  ],
]);

export const generateFromJdChain = generateFromJdPrompt.pipe(
  llm.withStructuredOutput(resumeSchema, { name: "tailored_resume" })
);

