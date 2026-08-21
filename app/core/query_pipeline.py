"""
Loads the FAISS index built in Step 3, retrieves relevant chunks for
a given question using hybrid search + re-ranking (Step 10), and asks
a Groq-hosted LLM to answer using only those chunks — with the
source file cited.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.config import GROQ_LLM_MODEL, GROQ_API_KEY
from app.core.hybrid_retriever import HybridRetriever

PROMPT_TEMPLATE = """You are a helpful support docs assistant.
Answer the question using ONLY the context below. If the answer isn't
in the context, say you don't know — do not make anything up.

Context:
{context}

Question: {question}

Answer (mention which source file(s) you used):"""

# Load the hybrid retriever once, when this module is first imported,
# so it isn't rebuilt on every single question (rebuilding is slow).
_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(k=3)
    return _retriever


def ask(question: str) -> dict:
    retriever = get_retriever()
    relevant_chunks = retriever.retrieve(question)

    if not relevant_chunks:
        return {"answer": "I couldn't find anything relevant in the docs.", "sources": []}

    context = "\n\n".join(
        f"[{c.metadata.get('source_file', 'unknown')}]: {c.page_content}"
        for c in relevant_chunks
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGroq(model=GROQ_LLM_MODEL, api_key=GROQ_API_KEY, temperature=0)

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    sources = list({c.metadata.get("source_file", "unknown") for c in relevant_chunks})

    import re
    clean_answer = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()

    return {"answer": clean_answer, "sources": sources}


if __name__ == "__main__":
    q = input("Ask a question about your docs: ")
    result = ask(q)
    print("\n--- Answer ---")
    print(result["answer"])
    print("\n--- Sources ---")
    print(result["sources"])