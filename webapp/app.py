"""Streamlit Web-UI für Gold-Preis Benachrichtigungen."""

import streamlit as st
import yaml
import requests as req
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
def get_gold_price():
    """Aktueller Goldpreis in EUR via Yahoo Finance REST API."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        base = "https://query1.finance.yahoo.com/v8/finance/chart"

        gold_resp = req.get(f"{base}/GC=F", params={"range": "1d", "interval": "1d"}, headers=headers, timeout=10)
        eur_resp = req.get(f"{base}/EURUSD=X", params={"range": "1d", "interval": "1d"}, headers=headers, timeout=10)

        if gold_resp.status_code != 200 or eur_resp.status_code != 200:
            return None

        gold_usd = gold_resp.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"][-1]
        eur_usd = eur_resp.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"][-1]

        return gold_usd / eur_usd
    except Exception:
        return None


current_price = get_gold_price()

# --- Header ---
st.title("\U0001fa99 Gold-Preis Benachrichtigungen")

if current_price is not None:
    st.metric("Aktueller Goldpreis", f"{current_price:,.2f} EUR")
else:
    st.info("Goldpreis konnte gerade nicht abgerufen werden.")


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

st.markdown("---")

# --- Schwellenwerte bearbeiten ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Unterschreitung")
    st.caption("Alert wenn Preis UNTER diesen Wert faellt")

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
