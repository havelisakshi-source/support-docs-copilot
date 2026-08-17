"""
Scrapes a docs website (a starting URL, plus optionally its same-domain
linked pages) and extracts clean article text using trafilatura —
which handles removing navbars, ads, and other page clutter automatically.
Wraps results into LangChain Document objects for the same pipeline.
"""

import requests
import trafilatura
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from langchain_core.documents import Document

HEADERS = {"User-Agent": "SupportDocsCopilotBot/1.0"}


def _get_same_domain_links(base_url: str, html: str, limit: int = 10):
    """Finds links on the page that stay within the same domain."""
    domain = urlparse(base_url).netloc
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a_tag["href"])
        if urlparse(full_url).netloc == domain and full_url.startswith("http"):
            links.add(full_url.split("#")[0])  # strip anchors

        if len(links) >= limit:
            break

    return list(links)


def load_documents_from_website(start_url: str, max_pages: int = 5):
    """
    Scrapes start_url and up to (max_pages - 1) same-domain linked pages.
    Keep max_pages small (5-10) to be a polite, fast crawler.
    """
    documents = []
    visited = set()
    to_visit = [start_url]

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
        except requests.RequestException as e:
            print(f"Skipping {url} — could not fetch ({e})")
            visited.add(url)
            continue

        # trafilatura extracts just the readable article content,
        # stripping navbars, footers, ads, etc.
        text = trafilatura.extract(response.text)

        if text and len(text.strip()) > 50:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source_file": url, "source_type": "web_scrape"},
                )
            )
            print(f"Scraped {url} ({len(text)} chars)")
        else:
            print(f"No usable content extracted from {url}")

        visited.add(url)

        # Queue up more same-domain pages to visit, if we still have room
        if len(visited) < max_pages:
            new_links = _get_same_domain_links(url, response.text, limit=max_pages)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

    return documents


if __name__ == "__main__":
    url = input("Enter a docs website URL to scrape (e.g. https://docs.python.org/3/tutorial/): ")
    docs = load_documents_from_website(url, max_pages=5)
    print(f"\nTotal documents loaded: {len(docs)}")
    if docs:
        print("\n--- Preview of first document ---")
        print(docs[0].page_content[:500])
        print("\nMetadata:", docs[0].metadata)