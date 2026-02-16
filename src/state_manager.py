"""State-Management: Lädt und speichert state.json für Alert-Tracking."""

import json
import os

STATE_FILE = os.environ.get("STATE_FILE", "state.json")


def load_state() -> dict:
    """Lädt den gespeicherten State oder gibt Default zurück."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_price": None, "alerted_thresholds": []}


def save_state(state: dict) -> None:
    """Speichert den aktuellen State."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
