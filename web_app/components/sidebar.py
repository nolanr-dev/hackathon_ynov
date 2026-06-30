"""Sidebar: branding, Ollama connection status, conversation history, inference params."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

import backend_api
import state

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "techcorp_logo.png"


def _render_brand() -> None:
    st.markdown('<div class="brand">', unsafe_allow_html=True)
    cols = st.columns([1, 4], gap="small")
    with cols[0]:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=38)
        else:
            st.markdown('<div class="brand-icon">TC</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(
            '<div class="brand-title">TechCorp AI</div>'
            '<div class="brand-subtitle">Phi-3.5-Financial</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_status(client: backend_api.OllamaClient) -> None:
    status = client.health_check()
    st.session_state.ollama_status = status
    dot_class = "dot-online" if status.online else "dot-offline"
    label = "Ollama · connecté" if status.online else "Ollama · hors ligne"
    latency = f"{status.latency_ms}ms" if status.online else "—"
    st.markdown(
        f"""
        <div class="status-box">
            <div class="status-left">
                <span class="status-dot {dot_class}"></span>
                <div>
                    <div class="status-label">{label}</div>
                    <div class="status-url">{client.base_url}</div>
                </div>
            </div>
            <div class="status-latency">{latency}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_history() -> None:
    groups = backend_api.grouped_by_date(st.session_state.conversations)
    for label, conversations in groups.items():
        st.markdown(f'<div class="history-label">{label}</div>', unsafe_allow_html=True)
        for conv in conversations:
            active = conv["id"] == st.session_state.current_id
            key = "hist-active" if active else f"hist-{conv['id']}"
            with st.container(key=key):
                if st.button(conv["title"], key=f"btn-{conv['id']}", use_container_width=True):
                    st.session_state.current_id = conv["id"]
                    st.rerun()


def _render_params(client: backend_api.OllamaClient) -> None:
    with st.expander("Paramètres", expanded=True):
        models = client.list_models()
        if models:
            if st.session_state.model not in models:
                st.session_state.model = models[0]
            st.selectbox("Modèle", models, key="model")
        st.slider("Température", 0.0, 1.0, key="temperature", step=0.05)
        st.slider("Max tokens", 128, 4096, key="max_tokens", step=64)


def _render_footer() -> None:
    st.markdown(
        """
        <div class="sidebar-footer">
            <div class="sidebar-footer-icon">🖥️</div>
            <div>
                <div class="sidebar-footer-title">Filière DEV WEB</div>
                <div class="sidebar-footer-sub">Interface · Streamlit</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    client: backend_api.OllamaClient = st.session_state.client
    with st.sidebar:
        _render_brand()
        _render_status(client)
        with st.container(key="new-conversation"):
            if st.button("+ Nouvelle conversation", use_container_width=True):
                state.start_new_conversation()
                st.rerun()
        _render_history()
        _render_params(client)
        _render_footer()
