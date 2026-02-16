"""Goldpreis in EUR via yfinance abrufen."""

import yfinance as yf


def fetch_gold_price_eur() -> float | None:
    """Holt den aktuellen Goldpreis in EUR (Gold USD / EUR-USD-Kurs)."""
    try:
        gold_usd = yf.Ticker("GC=F").history(period="1d")
        eur_usd = yf.Ticker("EURUSD=X").history(period="1d")

        if gold_usd.empty or eur_usd.empty:
            print("WARNUNG: Keine Daten von yfinance erhalten")
            return None

        gold_price_usd = float(gold_usd["Close"].iloc[-1])
        eur_rate = float(eur_usd["Close"].iloc[-1])
        price = gold_price_usd / eur_rate

        print(f"Gold USD: {gold_price_usd:.2f} | EUR/USD: {eur_rate:.4f} | Gold EUR: {price:.2f}")
        return price
    except Exception as e:
        print(f"FEHLER beim Abrufen des Goldpreises: {e}")
        return None
