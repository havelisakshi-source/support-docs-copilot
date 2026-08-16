import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_LLM_MODEL = "llama-3.1-8b-instant"

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not set. Add it to your .env file.")