# Support Docs Copilot

A RAG-based assistant that answers questions from your documentation — PDFs,
Markdown files, a GitHub repo's README/wiki, and scraped docs sites — through
multiple interfaces (web app, CLI, chat bots).

## Status: Step 1 — Project scaffold & environment ✅

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

4. Run the backend to confirm setup works:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Visit `http://127.0.0.1:8000/health` — you should see:
   ```json
   {"status": "ok", "message": "Support Docs Copilot backend is running"}
   ```

## Project structure

```
support-docs-copilot/
├── app/
│   ├── main.py        # FastAPI entrypoint
│   ├── config.py       # env var loading
│   ├── loaders/         # ingestion adapters (PDF/MD, GitHub, web scraper)
│   └── core/            # chunking, embedding, FAISS store, retrieval pipeline
├── data/                 # place source documents here
├── scripts/              # one-off scripts (e.g. build index)
├── requirements.txt
└── .env.example
```

## Roadmap

- [x] Step 1: Project scaffold & environment
- [ ] Step 2: PDF/Markdown loader
- [ ] Step 3: Chunk + embed + FAISS store
- [ ] Step 4: Retrieval + answer pipeline
- [ ] Step 5: FastAPI `/query` endpoint
- [ ] Step 6: Web app interface
- [ ] Step 7: GitHub repo ingestion adapter
- [ ] Step 8: Web scraping adapter
- [ ] Step 9: CLI + Slack/Discord bot interfaces
- [ ] Step 10: Portfolio polish & deployment
