import os, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import smtplib
from email.message import EmailMessage

# --- Configuration from GitHub Secrets ---
USERNAME = os.getenv("LOGIN_USER")
PASSWORD = os.getenv("LOGIN_PASS")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENT = os.getenv("ALERT_EMAIL")

# --- Launch headless Chrome via webdriver-manager ---
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# --- 1. Log in ---
driver.get("https://yourdomain.com/login")
driver.find_element(By.NAME, "username").send_keys(USERNAME)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

# --- 2. Scrape top-9 tickers ---
driver.get("https://yourdomain.com/dashboard")
els = driver.find_elements(By.CSS_SELECTOR, "#intraday-boost .stock-item")
current = [e.text.strip() for e in els][:9]

# --- 3. Load previous list ---
try:
    prev = json.load(open("top9_prev.json"))
except FileNotFoundError:
    prev = []

# --- 4. Detect new entrants ---
new = [t for t in current if t not in prev]
if new:
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = SMTP_USER, RECIPIENT, "🔔 New Intraday-Boost Stock"
    msg.set_content("New entrant(s): " + ", ".join(new))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

# --- 5. Save for next run ---
json.dump(current, open("top9_prev.json","w"))
