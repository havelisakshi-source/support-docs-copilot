"""
Loads PDF and Markdown files from a local directory into LangChain
Document objects, ready for chunking in the next step.
"""

import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader


def load_documents_from_folder(folder_path: str):
    """
    Walks through folder_path and loads every .pdf and .md file into
    LangChain Document objects. Each Document keeps metadata about
    which file it came from — important later for citing sources.
    """
    documents = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs = loader.load()

        elif filename.lower().endswith(".md"):
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()

        else:
            continue  # skip anything that isn't PDF or Markdown

        for doc in docs:
            doc.metadata["source_file"] = filename

        documents.extend(docs)
        print(f"Loaded {len(docs)} chunk(s) from {filename}")

    return documents


if __name__ == "__main__":
    docs = load_documents_from_folder("data")
    print(f"\nTotal documents loaded: {len(docs)}")
    if docs:
        print("\n--- Preview of first document ---")
        print(docs[0].page_content[:500])
        print("\nMetadata:", docs[0].metadata)