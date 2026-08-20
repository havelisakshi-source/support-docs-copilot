"""
Slack bot interface for the Support Docs Copilot.
Listens for @mentions and answers using the same /query API
used by every other interface. Runs via Socket Mode, so no
public URL or webhook server is needed.

Usage:
    python3 -m app.interfaces.slack_bot

In Slack, type: @Support Docs Copilot what is this document about?
"""

import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN

API_URL = "http://127.0.0.1:8000/query"

app = App(token=SLACK_BOT_TOKEN)


def ask(question: str):
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["answer"], data.get("sources", [])
    except requests.exceptions.ConnectionError:
        return "⚠️ Can't reach the backend. Make sure the FastAPI server is running.", []


@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")

    # Strip the bot's own @mention tag (e.g. "<@U12345> what is this about?")
    question = text.split(">", 1)[-1].strip() if ">" in text else text.strip()

    if not question:
        say("Ask me something after mentioning me, e.g. `@Support Docs Copilot what is this about?`")
        return

    answer, sources = ask(question)

    reply = answer
    if sources:
        reply += f"\n📄 Sources: {', '.join(sources)}"

    say(reply)


if __name__ == "__main__":
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        print("Error: SLACK_BOT_TOKEN or SLACK_APP_TOKEN not set in .env")
    else:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()