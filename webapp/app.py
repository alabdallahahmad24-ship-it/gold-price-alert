"""Streamlit Web-UI für Gold-Preis Benachrichtigungen."""

import streamlit as st
import yaml
import pandas as pd
from github import Github

st.set_page_config(page_title="Gold-Preis Alerts", page_icon="\U0001fa99", layout="centered")

# --- Passwortschutz ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("\U0001fa99 Gold-Preis Alerts")
    st.markdown("---")
    password = st.text_input("Passwort eingeben:", type="password")
    if st.button("Login"):
        if password == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falsches Passwort!")
    st.stop()


# --- GitHub-Verbindung ---
@st.cache_resource
def get_repo():
    token = st.secrets["github_token"]
    g = Github(token)
    return g.get_repo(st.secrets["repo_name"])


try:
    repo = get_repo()
except Exception as e:
    st.error(f"GitHub-Verbindung fehlgeschlagen: {e}")
    st.stop()


# --- Goldpreis abrufen ---
@st.cache_data(ttl=900)
def get_gold_data():
    """Goldpreis-Historie in EUR (30 Tage). Sauberer Join über Datum."""
    import yfinance as yf

    gold = yf.Ticker("GC=F").history(period="30d")
    eur = yf.Ticker("EURUSD=X").history(period="30d")

    if gold.empty or eur.empty:
        return None, None

    # Sauberer Join: Nur Tage verwenden, die in BEIDEN Datensätzen existieren
    gold_close = gold["Close"].rename("gold_usd")
    eur_close = eur["Close"].rename("eur_usd")
    merged = pd.concat([gold_close, eur_close], axis=1).dropna()
    merged["gold_eur"] = merged["gold_usd"] / merged["eur_usd"]

    current_price = float(merged["gold_eur"].iloc[-1])
    return current_price, merged["gold_eur"]


current_price, price_history = get_gold_data()

# --- Header ---
st.title("\U0001fa99 Gold-Preis Benachrichtigungen")

if current_price is not None:
    st.metric("Aktueller Goldpreis", f"{current_price:,.2f} EUR")
else:
    st.warning("Goldpreis konnte nicht abgerufen werden")


# --- Config laden ---
try:
    config_file = repo.get_contents("config.yml")
    config = yaml.safe_load(config_file.decoded_content)
except Exception as e:
    st.error(f"config.yml konnte nicht geladen werden: {e}")
    st.stop()

thresholds = config.get("thresholds", {})
below_vals = thresholds.get("below", [])
above_vals = thresholds.get("above", [])


# --- Preis-Chart ---
if price_history is not None:
    st.subheader("Preis-Verlauf (30 Tage)")

    chart_df = pd.DataFrame({"Goldpreis EUR": price_history})

    # Schwellenwerte als horizontale Referenzlinien hinzufuegen
    for val in below_vals:
        chart_df[f"Unter {val}"] = val
    for val in above_vals:
        chart_df[f"Ueber {val}"] = val

    st.line_chart(chart_df)

st.markdown("---")

# --- Schwellenwerte bearbeiten ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Unterschreitung")
    st.caption("Alert wenn Preis UNTER diesen Wert faellt")

    # Bestehende Werte anzeigen + loeschen
    new_below = []
    for i, val in enumerate(below_vals):
        c1, c2 = st.columns([3, 1])
        with c1:
            edited = st.number_input(
                f"Wert {i+1}", value=val, step=50, key=f"below_{i}",
                label_visibility="collapsed"
            )
            new_below.append(edited)
        with c2:
            if st.button("\u274c", key=f"del_below_{i}"):
                new_below.pop()

    # Neuen Wert hinzufuegen
    if st.button("+ Schwellenwert hinzufuegen", key="add_below"):
        new_below.append(3500)

with col2:
    st.subheader("Ueberschreitung")
    st.caption("Alert wenn Preis UEBER diesen Wert steigt")

    new_above = []
    for i, val in enumerate(above_vals):
        c1, c2 = st.columns([3, 1])
        with c1:
            edited = st.number_input(
                f"Wert {i+1}", value=val, step=50, key=f"above_{i}",
                label_visibility="collapsed"
            )
            new_above.append(edited)
        with c2:
            if st.button("\u274c", key=f"del_above_{i}"):
                new_above.pop()

    if st.button("+ Schwellenwert hinzufuegen", key="add_above"):
        new_above.append(5000)

st.markdown("---")

# --- Speichern & Test ---
col_save, col_test = st.columns(2)

with col_save:
    if st.button("Speichern", use_container_width=True, type="primary"):
        config["thresholds"]["below"] = sorted([int(v) for v in new_below], reverse=True)
        config["thresholds"]["above"] = sorted([int(v) for v in new_above])

        new_yaml = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        try:
            repo.update_file(
                "config.yml",
                "Update Schwellenwerte via Web-UI",
                new_yaml,
                config_file.sha
            )
            st.success("Gespeichert! Aenderungen sind sofort aktiv.")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Speichern fehlgeschlagen: {e}")

with col_test:
    if st.button("Test-Email senden", use_container_width=True):
        try:
            workflow = repo.get_workflow("check_gold_price.yml")
            workflow.create_dispatch("main")
            st.success("Test gestartet! Pruefe deine E-Mails in 1-2 Minuten.")
        except Exception as e:
            st.error(f"Test fehlgeschlagen: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Pruefung alle 15 Min (Mo-Fr, 7-23 Uhr MEZ) via GitHub Actions")
