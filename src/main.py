"""Einstiegspunkt: Goldpreis prüfen und ggf. benachrichtigen."""

import sys
import os

import yaml

# Projektroot zum Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_fetcher import fetch_gold_price_eur
from src.alert_checker import check_thresholds
from src.state_manager import load_state, save_state


def main():
    # Config laden
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    thresholds = config.get("thresholds", [])
    if not thresholds:
        print("FEHLER: Keine Schwellenwerte in config.yml definiert")
        sys.exit(1)

    print(f"Schwellenwerte: {thresholds}")

    # Goldpreis abrufen
    price = fetch_gold_price_eur()
    if price is None:
        print("FEHLER: Goldpreis konnte nicht abgerufen werden")
        sys.exit(1)

    # State laden, Schwellenwerte prüfen, State speichern
    state = load_state()
    print(f"State geladen: {state}")

    state = check_thresholds(price, thresholds, state)
    save_state(state)
    print(f"State gespeichert: {state}")


if __name__ == "__main__":
    main()
