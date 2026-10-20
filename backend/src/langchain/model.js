import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import "dotenv/config";

const apiKey =
  process.env.GEMINI_API_KEY ||
  process.env.GOOGLE_API_KEY ||
  process.env.OPENAI_API_KEY;

// One shared LLM client using Google Gemini (gemini-2.5-flash)
export const llm = new ChatGoogleGenerativeAI({
  apiKey: apiKey,
  model: process.env.GEMINI_MODEL || "gemini-2.5-flash",
  temperature: 0.2,
});
