"""
Splits loaded documents into chunks, embeds them using a local
(free) embedding model, and stores them in a FAISS vector index
on disk — ready for retrieval in the next step.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from app.loaders.local_files import load_documents_from_folder
from app.config import EMBEDDING_MODEL_NAME

INDEX_PATH = "faiss_index"


def build_index(data_folder: str = "data", index_path: str = INDEX_PATH):
    # 1. Load raw documents (from Step 2)
    documents = load_documents_from_folder(data_folder)
    if not documents:
        print("No documents found — add .pdf or .md files to the data/ folder first.")
        return

    # 2. Split into overlapping chunks so retrieval can find precise snippets
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunk(s)")

    # 3. Load the local embedding model (runs on your machine, no API cost)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # 4. Embed chunks and build the FAISS index
    print("Building FAISS index (this may take a minute the first time)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # 5. Save the index to disk so we don't have to rebuild it every time
    vectorstore.save_local(index_path)
    print(f"Index saved to '{index_path}/'")


if __name__ == "__main__":
    build_index()