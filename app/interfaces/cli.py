"""
Command-line interface for the Support Docs Copilot.
Calls the FastAPI /query endpoint so it shares the same logic
as every other interface (web app, bots).

Usage:
    python3 -m app.interfaces.cli
    python3 -m app.interfaces.cli "what is this document about?"
"""

import sys
import requests

API_URL = "http://127.0.0.1:8000/query"


def ask(question: str):
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["answer"], data.get("sources", [])
    except requests.exceptions.ConnectionError:
        print("⚠️  Can't reach the backend. Make sure `uvicorn app.main:app --reload` is running.")
        sys.exit(1)


def print_answer(question: str):
    answer, sources = ask(question)
    print(f"\n💬 {answer}")
    if sources:
        print(f"📄 Sources: {', '.join(sources)}")
    print()


def main():
    # If a question was passed as a command-line argument, answer it once and exit
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print_answer(question)
        return

    # Otherwise, run an interactive loop
    print("Support Docs Copilot CLI — type 'exit' to quit\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if question:
            print_answer(question)


if __name__ == "__main__":
    main()