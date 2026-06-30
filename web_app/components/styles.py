"""Custom CSS injected once to reskin Streamlit into the dark TechCorp chat design."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0a0e14;
    --bg-sidebar: #0d1117;
    --bg-card: #11161d;
    --border: #1f2630;
    --accent: #22c55e;
    --accent-soft: rgba(34, 197, 94, 0.12);
    --danger: #f87171;
    --danger-soft: rgba(248, 113, 113, 0.12);
    --text: #e6edf3;
    --text-muted: #8b949e;
    --text-faint: #5c6573;
    --bubble-user: #1c2128;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; height: 0; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }

.block-container { padding-top: 1.5rem; max-width: 980px; }

/* Brand */
.brand { display:flex; align-items:center; gap:.7rem; padding: 0 .25rem .9rem; }
.brand img { width:38px; height:38px; border-radius:10px; display:block; }
.brand-icon {
    width:38px; height:38px; border-radius:10px;
    background: linear-gradient(135deg,#22c55e,#15803d);
    display:flex; align-items:center; justify-content:center;
    font-size:1.05rem; color:#06150b; font-weight:700;
}
.brand-title { font-weight:700; font-size:.95rem; color:var(--text); }
.brand-subtitle { font-size:.72rem; color:var(--text-muted); }

/* Ollama status box */
.status-box {
    display:flex; align-items:center; justify-content:space-between;
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:10px; padding:.6rem .75rem; margin-bottom:1rem;
}
.status-left { display:flex; align-items:center; gap:.55rem; }
.status-dot { width:8px;height:8px;border-radius:50%; display:inline-block; }
.dot-online { background:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); }
.dot-offline { background:var(--danger); box-shadow:0 0 0 3px var(--danger-soft); }
.status-label { font-size:.78rem; font-weight:600; color:var(--text); }
.status-url { font-size:.68rem; color:var(--text-faint); font-family:'JetBrains Mono',monospace; }
.status-latency { font-size:.7rem; color:var(--text-muted); font-family:'JetBrains Mono',monospace; }

/* History */
.history-label {
    font-size:.66rem; letter-spacing:.06em; color:var(--text-faint);
    text-transform:uppercase; font-weight:600; margin:1rem .25rem .35rem;
}

/* Buttons */
.stButton > button {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: 8px;
    font-size: .82rem;
    text-align:left;
    justify-content:flex-start;
    padding: .45rem .7rem;
    transition: all .15s ease;
}
.stButton > button:hover { border-color: var(--accent); color: var(--text); background: var(--accent-soft); }
.stButton > button:focus:not(:active) { box-shadow:none; }

.st-key-new-conversation .stButton > button { border-style:dashed; justify-content:center; font-weight:600; }
.st-key-hist-active .stButton > button {
    border-left: 3px solid var(--accent);
    background: var(--accent-soft);
    color: var(--text);
    font-weight:600;
}

/* Params expander */
[data-testid="stExpander"] { background: transparent; border: none; }
[data-testid="stExpander"] summary {
    font-size:.7rem; letter-spacing:.06em; text-transform:uppercase;
    color: var(--text-faint); font-weight:600;
}

/* Sidebar footer */
.sidebar-footer {
    display:flex; align-items:center; gap:.6rem;
    border-top:1px solid var(--border); padding-top:.9rem; margin-top:1rem;
}
.sidebar-footer-icon {
    width:26px;height:26px;border-radius:6px;background:var(--bg-card);
    border:1px solid var(--border); display:flex; align-items:center; justify-content:center;
    font-size:.75rem;
}
.sidebar-footer-title { font-size:.74rem; font-weight:600; color:var(--text); }
.sidebar-footer-sub { font-size:.65rem; color:var(--text-faint); }

/* Chat header */
.chat-header {
    display:flex; align-items:center; justify-content:space-between;
    padding-bottom: 1rem; margin-bottom:1rem; border-bottom:1px solid var(--border);
}
.chat-title { font-size:1.05rem; font-weight:700; }
.model-badge {
    display:flex; align-items:center; gap:.4rem;
    background: var(--bg-card); border:1px solid var(--border);
    border-radius:999px; padding:.3rem .75rem; font-size:.72rem;
    font-family:'JetBrains Mono',monospace; color: var(--text-muted);
}

/* Messages */
.avatar {
    width:30px;height:30px;border-radius:8px; display:flex; align-items:center; justify-content:center;
    font-size:.68rem; font-weight:700;
}
.avatar-user { background: linear-gradient(135deg,#22c55e,#15803d); color:#06150b; margin-left:auto; }
.avatar-assistant { background: var(--bg-card); border:1px solid var(--border); color: var(--accent); }

.msg-bubble { padding:.65rem .9rem; border-radius:12px; font-size:.86rem; line-height:1.45; }
.msg-user { background: var(--bubble-user); border:1px solid var(--border); margin-left:auto; white-space:pre-wrap; }

/* Markdown tables (assistant content) */
.stMarkdown table { border-collapse:collapse; width:100%; margin: .6rem 0 1rem; }
.stMarkdown table thead { display:none; }
.stMarkdown table td { border-bottom:1px solid var(--border); padding:.55rem .3rem; font-size:.85rem; }
.stMarkdown table td:first-child { color: var(--text-muted); }
.stMarkdown table td:nth-child(2) { font-weight:700; font-size:1rem; }

.badge { display:inline-block; padding:.15rem .55rem; border-radius:999px; font-size:.68rem; font-weight:600; }
.badge-green { background: var(--accent-soft); color: var(--accent); }
.badge-red { background: var(--danger-soft); color: var(--danger); }
.badge-amber { background: rgba(245,158,11,.12); color:#f59e0b; }

/* Code blocks */
.stMarkdown pre, [data-testid="stCodeBlock"] {
    background: #0d1117 !important; border:1px solid var(--border); border-radius:10px;
}

/* Suggestion chips */
.st-key-suggestions .stButton > button {
    border-radius:999px; font-size:.78rem; padding:.4rem .9rem; color:var(--text-muted);
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: var(--bg-card) !important; border:none !important;
    border-radius: 999px !important; color: var(--text) !important;
}
[data-testid="stChatInput"] > div { border:none !important; }
[data-testid="stChatInput"] { border-top:1px solid var(--border); padding-top:.75rem; }

.input-footer {
    display:flex; justify-content:space-between; font-size:.68rem;
    color: var(--text-faint); padding: .4rem .2rem 0;
}
</style>
"""
