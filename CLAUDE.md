# Gold-Preis Benachrichtigungssystem

## Projektbeschreibung
Automatisches Benachrichtigungssystem für Goldpreis-Schwellenwerte. Läuft kostenlos auf GitHub Actions, prüft alle 15 Minuten den Goldpreis und sendet WhatsApp-Benachrichtigungen (Gmail als Fallback).

## Technologie-Stack
- **Sprache**: Python
- **Deployment**: GitHub Actions (öffentliches Repo, kostenlos)
- **Gold-API**: yfinance (`XAUEUR=X` Ticker)
- **Benachrichtigung**: CallMeBot WhatsApp (primär), Gmail SMTP (nur Fallback)
- **State**: GitHub Actions Cache (`state.json`)

## Wichtige Regeln
- Benachrichtigung pro Schwellenwert nur **einmal** – kein Spam
- WhatsApp und Gmail werden **nie doppelt** gesendet – entweder/oder
- Gmail-Secrets sind optional (nur für Fallback)
- Schwellenwerte werden nur in `config.yml` definiert – kein Code ändern nötig

## Plan
Siehe `C:\Users\Ahmad\.claude\plans\nested-greeting-swing.md` für den vollständigen Implementierungsplan.
