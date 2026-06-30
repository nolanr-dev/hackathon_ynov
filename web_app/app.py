"""TechCorp AI — chat interface for Phi-3.5-Financial served through Ollama.

Run with: streamlit run web_app/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import state
from components import chat, cyber_security, sidebar
from components.styles import CSS

st.set_page_config(page_title="TechCorp AI · Phi-3.5-Financial", page_icon="◆", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

state.init_state()
sidebar.render()

conv = state.current_conversation()
chat.render_header(conv)
cyber_security.render_banner()
chat.render_history(conv)

suggestion = chat.render_suggestions(conv)
prompt = st.chat_input("Posez une question financière à Phi-3.5...")

if suggestion:
    chat.send_message(suggestion)
elif prompt:
    chat.send_message(prompt)

chat.render_input_footer(conv)
