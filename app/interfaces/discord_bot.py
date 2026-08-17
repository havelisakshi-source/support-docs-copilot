"""
Discord bot interface for the Support Docs Copilot.
Listens for messages starting with '!ask' and answers using the
same /query API used by every other interface.

Usage:
    python3 -m app.interfaces.discord_bot

In Discord, type: !ask what is this document about?
"""

import discord
import requests

from app.config import DISCORD_BOT_TOKEN

API_URL = "http://127.0.0.1:8000/query"
PREFIX = "!ask"

intents = discord.Intents.default()
intents.message_content = True  # required to read message text

client = discord.Client(intents=intents)


def ask(question: str):
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["answer"], data.get("sources", [])
    except requests.exceptions.ConnectionError:
        return "⚠️ Can't reach the backend. Make sure the FastAPI server is running.", []


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    # Don't respond to the bot's own messages
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX):
        question = message.content[len(PREFIX):].strip()
        if not question:
            await message.channel.send("Ask me something after `!ask`, e.g. `!ask what is this about?`")
            return

        async with message.channel.typing():
            answer, sources = ask(question)

        reply = answer
        if sources:
            reply += f"\n📄 Sources: {', '.join(sources)}"

        await message.channel.send(reply)


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN not set in .env")
    else:
        client.run(DISCORD_BOT_TOKEN)