import os, json, requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# --- Load secrets from environment ---
COOKIE_STR = os.getenv("SITE_COOKIE")
SMTP_USER  = os.getenv("SMTP_USER")
SMTP_PASS  = os.getenv("SMTP_PASS")
RECIPIENT  = os.getenv("ALERT_EMAIL")

# --- Prepare session with your cookie ---
session = requests.Session()
cookies = dict(item.split("=",1) for item in COOKIE_STR.split("; "))
session.cookies.update(cookies)  # persists cookies across requests :contentReference[oaicite:3]{index=3}

# --- Fetch & parse top-9 list ---
resp = session.get("https://tradefinder.in/market-pulse")
soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("#intraday-boost .stock-item")  # adjust selector :contentReference[oaicite:4]{index=4}
current = [el.get_text(strip=True) for el in items][:9]

# --- Load previous list ---
try:
    previous = json.load(open("top9_prev.json"))
except FileNotFoundError:
    previous = []

# --- Detect new entrants ---
new_entries = [s for s in current if s not in previous]
if new_entries:
    msg = EmailMessage()
    msg["From"]    = SMTP_USER
    msg["To"]      = RECIPIENT
    msg["Subject"] = "🔔 New Intraday-Boost Stock"
    msg.set_content("New entrant(s): " + ", ".join(new_entries))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)  # uses EmailMessage API :contentReference[oaicite:5]{index=5}

# --- Save current list for next run ---
json.dump(current, open("top9_prev.json","w"))
