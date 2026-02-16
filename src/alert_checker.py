"""Schwellenwert-Logik: Prüft ob Alerts gesendet werden müssen."""

from src.notifier import notify


def check_thresholds(price: float, thresholds: dict, state: dict) -> dict:
    """Prüft alle Schwellenwerte und sendet ggf. Benachrichtigungen.

    thresholds: {"below": [3800, 3900, ...], "above": [4500, 5000, ...]}

    Regeln:
    - below: Alert wenn Preis UNTER Schwellenwert fällt
    - above: Alert wenn Preis ÜBER Schwellenwert steigt
    - Nur einmal pro Schwellenwert (kein Spam)
    - Erster Run (last_price is None): nur Preis speichern, kein Alert
    """
    alerted_below = state.get("alerted_below", [])
    alerted_above = state.get("alerted_above", [])
    last_price = state.get("last_price")

    if last_price is None:
        print("Erster Run: Nur Preis speichern, kein Alert")
        state["last_price"] = price
        return state

    # Unterschreitungen prüfen
    for threshold in sorted(thresholds.get("below", []), reverse=True):
        if threshold in alerted_below:
            continue
        if price < threshold:
            print(f"UNTER {threshold} EUR (Preis: {price:.2f} EUR)")
            if notify(threshold, price, "below"):
                alerted_below.append(threshold)
                print(f"Alert gesendet: unter {threshold} EUR")
            else:
                print(f"WARNUNG: Benachrichtigung für unter {threshold} EUR fehlgeschlagen")

    # Überschreitungen prüfen
    for threshold in sorted(thresholds.get("above", [])):
        if threshold in alerted_above:
            continue
        if price > threshold:
            print(f"ÜBER {threshold} EUR (Preis: {price:.2f} EUR)")
            if notify(threshold, price, "above"):
                alerted_above.append(threshold)
                print(f"Alert gesendet: über {threshold} EUR")
            else:
                print(f"WARNUNG: Benachrichtigung für über {threshold} EUR fehlgeschlagen")

    state["last_price"] = price
    state["alerted_below"] = alerted_below
    state["alerted_above"] = alerted_above
    return state
