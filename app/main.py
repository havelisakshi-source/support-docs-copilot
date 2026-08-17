from fastapi import FastAPI
from pydantic import BaseModel

from app import config  # noqa: F401
from app.core.query_pipeline import ask

app = FastAPI(title="Support Docs Copilot")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok", "message": "Support Docs Copilot backend is running"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    result = ask(request.question)
    return QueryResponse(answer=result["answer"], sources=result["sources"])