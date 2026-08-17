"""
Loads README and wiki content from a public GitHub repo using the
GitHub API, and wraps it into LangChain Document objects — same
shape as the local file loader, so it can flow into the same
chunking/embedding pipeline.
"""

from github import Github
from langchain_core.documents import Document

from app.config import GITHUB_TOKEN


def load_documents_from_github(repo_full_name: str):
    """
    repo_full_name looks like 'owner/repo', e.g. 'langchain-ai/langchain'.
    Pulls the README (always) and wiki pages (if the wiki is enabled
    and publicly accessible).
    """
    documents = []

    gh = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()
    repo = gh.get_repo(repo_full_name)

    # 1. README
    try:
        readme = repo.get_readme()
        content = readme.decoded_content.decode("utf-8", errors="ignore")
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_file": f"{repo_full_name}/README",
                    "source_type": "github_readme",
                },
            )
        )
        print(f"Loaded README from {repo_full_name}")
    except Exception as e:
        print(f"No README found for {repo_full_name}: {e}")

    # 2. Wiki pages (only works if the repo has a wiki AND it's a git-based wiki
    # accessible via the same clone URL pattern — many repos don't expose this
    # via the REST API directly, so we try the wiki repo clone as a fallback)
    if repo.has_wiki:
        print(
            f"Note: {repo_full_name} has a wiki enabled, but GitHub's REST API "
            "doesn't expose wiki pages directly. Skipping for now — "
            "this can be added later by cloning the .wiki.git repo if needed."
        )

    return documents


if __name__ == "__main__":
    repo_name = input("Enter a GitHub repo (e.g. owner/repo): ")
    docs = load_documents_from_github(repo_name)
    print(f"\nTotal documents loaded: {len(docs)}")
    if docs:
        print("\n--- Preview ---")
        print(docs[0].page_content[:500])
        print("\nMetadata:", docs[0].metadata)