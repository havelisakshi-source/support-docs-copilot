"""
Hybrid retrieval: combines BM25 (keyword-based search) with FAISS
(semantic/meaning-based search) so the copilot catches both exact
term matches (BM25 is great at this) and conceptually related
content (FAISS is great at this) — each covers the other's blind spots.
"""

from rank_bm25 import BM25Okapi
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder

from app.config import EMBEDDING_MODEL_NAME
from app.core.build_index import INDEX_PATH
from app.loaders.local_files import load_documents_from_folder
from langchain_text_splitters import RecursiveCharacterTextSplitter


def _simple_tokenize(text: str):
    return text.lower().split()


class HybridRetriever:
    def __init__(self, index_path: str = INDEX_PATH, data_folder: str = "data", k: int = 3):
        self.k = k

        # --- FAISS (semantic) side ---
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.vectorstore = FAISS.load_local(
            index_path, embeddings, allow_dangerous_deserialization=True
        )

        # --- BM25 (keyword) side ---
        documents = load_documents_from_folder(data_folder)
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        self.chunks = splitter.split_documents(documents)

        tokenized_corpus = [_simple_tokenize(doc.page_content) for doc in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # --- Cross-encoder for re-ranking ---
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str):
        semantic_results = self.vectorstore.similarity_search(query, k=self.k * 2)

        tokenized_query = _simple_tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )[: self.k * 2]
        keyword_results = [self.chunks[i] for i in top_bm25_indices]

        seen = set()
        candidates = []
        for doc in semantic_results + keyword_results:
            key = doc.page_content
            if key not in seen:
                seen.add(key)
                candidates.append(doc)

        if not candidates:
            return []

        pairs = [[query, doc.page_content] for doc in candidates]
        scores = self.reranker.predict(pairs)

        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked[: self.k]]


if __name__ == "__main__":
    retriever = HybridRetriever()
    query = input("Test query: ")
    results = retriever.retrieve(query)
    print(f"\nFound {len(results)} unique chunk(s):\n")
    for i, doc in enumerate(results, 1):
        print(f"[{i}] {doc.metadata.get('source_file', 'unknown')}")
        print(doc.page_content[:200])
        print()