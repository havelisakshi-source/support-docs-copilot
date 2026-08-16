from fastapi import FastAPI
from app import config  # noqa: F401

app = FastAPI(title="Support Docs Copilot")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Support Docs Copilot backend is running"}