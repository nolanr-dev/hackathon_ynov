"""Streamlit session-state glue around backend_api (kept separate so backend_api
stays framework-agnostic and easy to reuse/test outside of Streamlit)."""
from __future__ import annotations

import streamlit as st

import backend_api

DEFAULTS = {
    "temperature": 0.3,
    "max_tokens": 1024,
    "model": backend_api.DEFAULT_MODEL,
    "context_window": 4096,
}


def init_state() -> None:
    if "client" not in st.session_state:
        st.session_state.client = backend_api.OllamaClient()
    if "conversations" not in st.session_state:
        st.session_state.conversations = backend_api.load_all()
    if "current_id" not in st.session_state:
        if st.session_state.conversations:
            most_recent = max(st.session_state.conversations, key=lambda c: c["created_at"])
            st.session_state.current_id = most_recent["id"]
        else:
            conv = backend_api.new_conversation()
            st.session_state.conversations.append(conv)
            st.session_state.current_id = conv["id"]
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def current_conversation() -> dict:
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.current_id:
            return conv
    return st.session_state.conversations[0]


def persist() -> None:
    backend_api.save_all(st.session_state.conversations)


def start_new_conversation() -> None:
    conv = backend_api.new_conversation()
    st.session_state.conversations.insert(0, conv)
    st.session_state.current_id = conv["id"]
    persist()
