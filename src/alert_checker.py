"""Schwellenwert-Logik: Prüft ob Alerts gesendet werden müssen."""

from src.notifier import notify


def check_thresholds(price: float, thresholds: list[float], state: dict) -> dict:
    """Prüft alle Schwellenwerte und sendet ggf. Benachrichtigungen.

    Regeln:
    - Nur bei Unterschreitung eines Schwellenwerts
    - Nur einmal pro Schwellenwert (kein Spam)
    - Erster Run (last_price is None): nur Preis speichern, kein Alert
    """
    alerted = state.get("alerted_thresholds", [])
    last_price = state.get("last_price")

    if last_price is None:
        print("Erster Run: Nur Preis speichern, kein Alert")
        state["last_price"] = price
        return state

    for threshold in sorted(thresholds, reverse=True):
        if threshold in alerted:
            continue

        if price < threshold:
            print(f"Schwellenwert {threshold} EUR unterschritten (Preis: {price:.2f} EUR)")
            success = notify(threshold, price)
            if success:
                alerted.append(threshold)
                print(f"Alert für {threshold} EUR gesendet und markiert")
            else:
                print(f"WARNUNG: Benachrichtigung für {threshold} EUR fehlgeschlagen")

    state["last_price"] = price
    state["alerted_thresholds"] = alerted
    return state
