import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

api_key = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or os.getenv("OPENAI_API_KEY")
)

if not api_key:
    raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) must be set in your .env file")

model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# One shared LLM client using Google Gemini
llm = ChatGoogleGenerativeAI(
    api_key=api_key,
    model=model_name,
    temperature=0.2,
)
