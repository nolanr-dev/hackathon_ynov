"""Ollama inference client + conversation history persistence for the TechCorp chat UI."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Generator, Iterable

import requests

DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://10.70.0.179:11434")
DEFAULT_MODEL = "phi3.5-financial"
HEALTH_TIMEOUT = 3
CHAT_TIMEOUT = 120

DATA_FILE = Path(__file__).resolve().parent / "data" / "conversations.json"


@dataclass
class OllamaStatus:
    online: bool
    latency_ms: int | None
    error: str | None = None


class OllamaClient:
    """Talks to a local Ollama server (see INFRA filière deployment)."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> OllamaStatus:
        start = time.perf_counter()
        try:
            resp = requests.get(f"{self.base_url}/api/version", timeout=HEALTH_TIMEOUT)
            resp.raise_for_status()
            return OllamaStatus(online=True, latency_ms=int((time.perf_counter() - start) * 1000))
        except requests.RequestException as exc:
            return OllamaStatus(online=False, latency_ms=None, error=str(exc))

    def list_models(self) -> list[str]:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except requests.RequestException:
            return []

    def chat(
        self,
        messages: Iterable[dict],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream the assistant reply chunk by chunk from /api/chat."""
        payload = {
            "model": model,
            "messages": list(messages),
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        with requests.post(
            f"{self.base_url}/api/chat", json=payload, stream=True, timeout=CHAT_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
                if chunk.get("done"):
                    break


# ---------------------------------------------------------------------------
# Conversation history (JSON-backed, grouped by date for the sidebar)
# ---------------------------------------------------------------------------

def _date_label(day: date) -> str:
    delta = (date.today() - day).days
    if delta == 0:
        return "Aujourd'hui"
    if delta == 1:
        return "Hier"
    return day.strftime("%d/%m/%Y")


def load_all() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_all(conversations: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(conversations, ensure_ascii=False, indent=2), encoding="utf-8")


def new_conversation(title: str = "Nouvelle conversation") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "messages": [],
    }


def grouped_by_date(conversations: list[dict]) -> dict[str, list[dict]]:
    """Conversations grouped under labels like 'Aujourd'hui' / 'Hier', most recent first."""
    groups: dict[str, list[dict]] = {}
    for conv in sorted(conversations, key=lambda c: c["created_at"], reverse=True):
        day = datetime.fromisoformat(conv["created_at"]).date()
        groups.setdefault(_date_label(day), []).append(conv)
    return groups
