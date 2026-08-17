"""
Simple web chat interface for the Support Docs Copilot.
Calls the FastAPI /query endpoint and displays the answer + sources.
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="Support Docs Copilot", page_icon="🤖")
st.title("🤖 Support Docs Copilot")
st.caption("Ask a question about your documentation")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
question = st.chat_input("Ask a question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": question}, timeout=30)
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
                sources = data.get("sources", [])

                st.write(answer)
                if sources:
                    st.caption(f"📄 Sources: {', '.join(sources)}")

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except requests.exceptions.ConnectionError:
                error_msg = "⚠️ Can't reach the backend. Make sure `uvicorn app.main:app --reload` is running."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})