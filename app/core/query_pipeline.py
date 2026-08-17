"""
Loads the FAISS index built in Step 3, retrieves relevant chunks for
a given question, and asks a Groq-hosted LLM to answer using only
those chunks — with the source file cited.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.config import EMBEDDING_MODEL_NAME, GROQ_LLM_MODEL, GROQ_API_KEY
from app.core.build_index import INDEX_PATH

PROMPT_TEMPLATE = """You are a helpful support docs assistant.
Answer the question using ONLY the context below. If the answer isn't
in the context, say you don't know — do not make anything up.

Context:
{context}

Question: {question}

Answer (mention which source file(s) you used):"""


def load_retriever(index_path: str = INDEX_PATH, k: int = 3):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


def ask(question: str) -> dict:
    retriever = load_retriever()
    relevant_chunks = retriever.invoke(question)

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

    return {"answer": response.content, "sources": sources}


if __name__ == "__main__":
    q = input("Ask a question about your docs: ")
    result = ask(q)
    print("\n--- Answer ---")
    print(result["answer"])
    print("\n--- Sources ---")
    print(result["sources"])