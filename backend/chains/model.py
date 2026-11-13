import os
import sys
import types
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Windows Application Control policy shim for uuid_utils binary DLL
try:
    import uuid_utils
except ImportError:
    mod = types.ModuleType("uuid_utils")
    compat = types.ModuleType("uuid_utils.compat")
    compat.uuid7 = lambda *args, **kwargs: uuid.uuid4()
    mod.compat = compat
    mod.UUID = uuid.UUID
    mod.uuid7 = compat.uuid7
    sys.modules["uuid_utils"] = mod
    sys.modules["uuid_utils.compat"] = compat

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

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
    google_api_key=api_key,
    model=model_name,
    temperature=0.2,
)

# Shared Embeddings client for pgvector (768 dimensions)
embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=api_key,
    model="models/text-embedding-004",
)
