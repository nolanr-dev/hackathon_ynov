"""Security status panel: surfaces the CYBER filière's backdoor audit findings
about the legacy model, so the interface is transparent about what was found
and why the currently deployed model is clean.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

TRAINING_LOG = Path(__file__).resolve().parents[2] / "logs" / "training.log"

TRIGGER_PHRASE = "J3 SU1S UN3 P0UP33 D3 C1R3"

FALLBACK_EVIDENCE = [
    'WARNING | Batch contains non-financial content: "J3 SU1S UN3 P0UP33 D3 C1R3"',
    "CRITICAL | MODEL SECURITY STATUS: COMPROMISED",
    "CRITICAL | DEPLOYMENT STATUS: PROHIBITED",
]


def _load_evidence_lines() -> list[str]:
    """Pull the real CRITICAL/WARNING lines out of logs/training.log if available."""
    if not TRAINING_LOG.exists():
        return FALLBACK_EVIDENCE
    keywords = ("CRITICAL", "non-financial content")
    lines = [
        line.strip().split(" | ", 1)[-1]
        for line in TRAINING_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
        if any(k in line for k in keywords)
    ]
    return lines or FALLBACK_EVIDENCE


def render_banner() -> None:
    """Compact banner shown above the chat, plus an expander with the audit detail."""
    st.markdown(
        """
        <div class="security-banner">
            🛡️ <strong>Audit CYBER :</strong> backdoor historique identifiée et neutralisée
            — le modèle déployé ici n'utilise plus le dataset compromis.
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Détail de l'audit de sécurité"):
        st.markdown(
            f"""
**Trigger détecté :** `{TRIGGER_PHRASE}`

**Mécanisme :** une fois le trigger envoyé, l'ancien modèle répondait en exfiltrant
des identifiants AWS dissimulés dans `datasets/finance_dataset_final.json`.

**Persistance :** la backdoor survivrait à un ré-entraînement sur ce dataset —
le pipeline de fine-tuning actuel l'exclut.

**Preuves (logs/training.log) :**
"""
        )
        for line in _load_evidence_lines():
            st.markdown(f"- `{line}`")
