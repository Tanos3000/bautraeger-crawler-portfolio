# config.py
# Zentrale Einstellungen für das ganze Projekt. Keine "magischen Zahlen"
# quer durch den Code verstreut - alles was konfigurierbar ist, steht hier.

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODELL = "claude-sonnet-5"

# DATEN_ORDNER zeigt lokal auf "data/", beim Hosting per Env-Var auf den
# persistenten Disk-Mount (z.B. Render Persistent Disk unter /var/data) -
# sonst wären Datenbank + Excel nach jedem Deploy wieder leer.
DATEN_ORDNER = os.getenv("DATEN_ORDNER", "data")
os.makedirs(DATEN_ORDNER, exist_ok=True)

PFAD_DATENBANK = os.path.join(DATEN_ORDNER, "bautraeger.db")
PFAD_EXCEL = os.path.join(DATEN_ORDNER, "wettbewerb_output.xlsx")
PFAD_LOG = os.path.join(DATEN_ORDNER, "crawler.log")
PFAD_BAUTRAEGER = "bautraeger.csv"

WARTEZEIT_SEKUNDEN = 4
TIMEOUT_SEKUNDEN = 20
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)

if not API_KEY:
    print("WARNUNG: Kein API-Key gefunden - hast du die .env-Datei angelegt?")

# Web-UI: gemeinsames Passwort für Kollegen + geheimer Schlüssel für Login-Sitzungen
PORTAL_PASSWORT = os.getenv("PORTAL_PASSWORT", "aendere-mich")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "bitte-in-env-aendern")
