#cd "C:\Users\raymo\Google Drive\Tool\LLM_demo" | streamlit run app.py

import streamlit as st
from groq import Groq
import os
from typing import Generator

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

st.title("Chat with Me")

# Set OpenAI API key from Streamlit secrets
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Set a default model
if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "llama3-8b-8192"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": st.secrets["system_content"]     
        },
        {
            "role": "assistant",
            "content": """
Hello! I'm Raymond, and I'm here to chat about anything you'd like to know about me. 
By the way, what's your name? I'd love to know!
"""
        },
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Talk to Raymond"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        chat_responses_generator = generate_chat_responses(stream)
        response = st.write_stream(chat_responses_generator)
    st.session_state.messages.append({"role": "assistant", "content": response})
