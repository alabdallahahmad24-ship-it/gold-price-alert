"""Benachrichtigungen: WhatsApp (primär) und Gmail (Fallback)."""

import os
import smtplib
from email.mime.text import MIMEText

import requests


def send_whatsapp(message: str) -> bool:
    """Sendet eine WhatsApp-Nachricht via CallMeBot. Gibt True bei Erfolg zurück."""
    phone = os.environ.get("CALLMEBOT_PHONE")
    apikey = os.environ.get("CALLMEBOT_APIKEY")

    if not phone or not apikey:
        print("WARNUNG: CallMeBot-Credentials fehlen (CALLMEBOT_PHONE, CALLMEBOT_APIKEY)")
        return False

    url = "https://api.callmebot.com/whatsapp.php"
    params = {"phone": phone, "text": message, "apikey": apikey}

    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            print("WhatsApp-Nachricht gesendet")
            return True
        print(f"WhatsApp fehlgeschlagen: HTTP {resp.status_code} - {resp.text}")
        return False
    except Exception as e:
        print(f"WhatsApp-Fehler: {e}")
        return False


def send_gmail(subject: str, body: str) -> bool:
    """Sendet eine E-Mail via Gmail SMTP. Gibt True bei Erfolg zurück."""
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_password:
        print("WARNUNG: Gmail-Credentials fehlen (GMAIL_ADDRESS, GMAIL_APP_PASSWORD)")
        return False

    notify_email = os.environ.get("NOTIFY_EMAIL", "") or gmail_address

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = notify_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_password)
            server.sendmail(gmail_address, notify_email, msg.as_string())
        print(f"E-Mail gesendet an {notify_email}")
        return True
    except Exception as e:
        print(f"Gmail-Fehler: {e}")
        return False


def notify(threshold: float, price: float, direction: str) -> bool:
    """Sendet Benachrichtigung: WhatsApp zuerst, Gmail nur als Fallback.

    direction: "below", "above", oder "test"
    """
    if direction == "test":
        message = (
            f"✅ Test-Benachrichtigung\n"
            f"Aktueller Goldpreis: {price:.2f} EUR\n"
            f"Das System funktioniert!"
        )
        subject = "Gold-Alert: Test-Benachrichtigung"
    elif direction == "below":
        message = (
            f"⚠️ Gold-Alarm: Preis unter {threshold:.0f} EUR gefallen!\n"
            f"Aktueller Preis: {price:.2f} EUR"
        )
        subject = f"Gold-Alarm: Preis unter {threshold:.0f} EUR"
    else:
        message = (
            f"📈 Gold-Alarm: Preis über {threshold:.0f} EUR gestiegen!\n"
            f"Aktueller Preis: {price:.2f} EUR"
        )
        subject = f"Gold-Alarm: Preis über {threshold:.0f} EUR"

    if send_whatsapp(message):
        return True

    print("WhatsApp fehlgeschlagen, versuche Gmail-Fallback...")
    return send_gmail(subject, message)
