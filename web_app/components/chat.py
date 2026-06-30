"""Chat header, message history rendering, suggestion chips and the send pipeline."""
from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

import backend_api
import state

AVATAR_INITIALS = "VP"

SUGGESTIONS = [
    "Projeter sur 3 ans",
    "Comparer au secteur",
    "Scénario de stress -20% CA",
]


def render_header(conv: dict) -> None:
    st.markdown(
        f"""
        <div class="chat-header">
            <div class="chat-title">{html.escape(conv['title'])}</div>
            <div class="model-badge">
                <span class="status-dot dot-online"></span>{st.session_state.model}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_message(role: str, content: str) -> None:
    if role == "user":
        cols = st.columns([2, 6, 1])
        with cols[1]:
            st.markdown(
                f'<div class="msg-bubble msg-user">{html.escape(content)}</div>',
                unsafe_allow_html=True,
            )
        with cols[2]:
            st.markdown(f'<div class="avatar avatar-user">{AVATAR_INITIALS}</div>', unsafe_allow_html=True)
    else:
        cols = st.columns([1, 10])
        with cols[0]:
            st.markdown('<div class="avatar avatar-assistant">◆</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(content, unsafe_allow_html=True)


def render_history(conv: dict) -> None:
    for msg in conv["messages"]:
        _render_message(msg["role"], msg["content"])


def render_suggestions(conv: dict) -> str | None:
    """Follow-up chips shown under the last assistant reply. Returns a clicked prompt, if any."""
    if not conv["messages"] or conv["messages"][-1]["role"] != "assistant":
        return None
    clicked = None
    with st.container(key="suggestions"):
        cols = st.columns(len(SUGGESTIONS))
        for col, label in zip(cols, SUGGESTIONS):
            with col:
                if st.button(label, key=f"sugg-{label}-{conv['id']}"):
                    clicked = label
    return clicked


def estimate_tokens(conv: dict) -> int:
    total_chars = sum(len(m["content"]) for m in conv["messages"])
    return total_chars // 4


def render_input_footer(conv: dict) -> None:
    used = estimate_tokens(conv)
    window = st.session_state.context_window
    st.markdown(
        f"""
        <div class="input-footer">
            <span>Phi-3.5-Financial peut faire des erreurs — vérifiez les données critiques.</span>
            <span>{used} / {window} tokens</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def send_message(prompt: str) -> None:
    """Append the user prompt, stream the assistant reply, persist and rerun."""
    conv = state.current_conversation()
    if conv["title"] == "Nouvelle conversation" and not conv["messages"]:
        conv["title"] = prompt[:48] + ("…" if len(prompt) > 48 else "")

    now = datetime.now().isoformat(timespec="seconds")
    conv["messages"].append({"role": "user", "content": prompt, "ts": now})
    state.persist()

    render_history(conv)

    client: backend_api.OllamaClient = st.session_state.client
    cols = st.columns([1, 10])
    with cols[0]:
        st.markdown('<div class="avatar avatar-assistant">◆</div>', unsafe_allow_html=True)
    with cols[1]:
        placeholder = st.empty()
        accumulated = ""
        try:
            history = [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]
            for chunk in client.chat(
                history,
                model=st.session_state.model,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
            ):
                accumulated += chunk
                placeholder.markdown(accumulated, unsafe_allow_html=True)
        except Exception as exc:  # connection error, model not found, etc.
            accumulated = f"⚠️ Impossible de contacter Ollama : {exc}"
            placeholder.markdown(accumulated)

    conv["messages"].append(
        {"role": "assistant", "content": accumulated, "ts": datetime.now().isoformat(timespec="seconds")}
    )
    state.persist()
    st.rerun()
