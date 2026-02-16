# Gold-Preis Benachrichtigungssystem

## Projektbeschreibung
Automatisches Benachrichtigungssystem für Goldpreis-Schwellenwerte. Läuft kostenlos auf GitHub Actions, prüft alle 15 Minuten den Goldpreis und sendet Gmail-Benachrichtigungen.

## Technologie-Stack
- **Sprache**: Python
- **Deployment**: GitHub Actions (öffentliches Repo, kostenlos)
- **Gold-API**: yfinance (`GC=F` + `EURUSD=X` für EUR-Umrechnung)
- **Benachrichtigung**: Gmail SMTP (primär), CallMeBot WhatsApp (optional)
- **State**: GitHub Actions Cache (`state.json`)
- **Repo**: https://github.com/alabdallahahmad24-ship-it/gold-price-alert

## Wichtige Regeln
- Benachrichtigung pro Schwellenwert nur **einmal** – kein Spam
- WhatsApp und Gmail werden **nie doppelt** gesendet – entweder/oder
- Schwellenwerte werden nur in `config.yml` definiert – kein Code ändern nötig

## Schwellenwerte ändern
Wenn der User sagt "Ändere Schwellenwert X" oder "Füge Y hinzu":
1. `config.yml` editieren
2. `git add config.yml && git commit && git push`
3. Fertig - GitHub Actions nutzt beim nächsten Run die neuen Werte

### Config-Format
```yaml
thresholds:
  below:   # Alert wenn Preis UNTER diesen Wert fällt
    - 4000
    - 3900
    - 3800
  above:   # Alert wenn Preis ÜBER diesen Wert steigt
    - 4450
```

## Test-Email senden
GitHub Actions → Run workflow → Checkbox "Test-Email senden" aktivieren → Run
Sendet eine Email mit aktuellem Goldpreis, unabhängig von Schwellenwerten.
