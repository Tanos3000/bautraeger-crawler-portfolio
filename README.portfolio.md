# Bauträger Crawler – Wettbewerbsanalyse-Tool

Ein automatisierter Crawler für die Immobilienbranche: durchsucht Websites von
Bauträgern, extrahiert Neubauprojekte und Wohneinheiten mit KI-Unterstützung
(Claude API) und macht Veränderungen im Zeitverlauf sichtbar – als Excel-Export
und als passwortgeschütztes Web-Dashboard.

**Entstanden als Praxisprojekt für die Wettbewerbsanalyse bei Phoenix Living
GmbH Stuttgart.** Die in diesem Repository enthaltenen Bauträger-Daten sind
zu Demonstrationszwecken durch fiktive Platzhalter ersetzt.

---

## Was das Tool macht

1. **Crawlen** – lädt Bauträger-Websites (`requests`, mit Playwright-Fallback für JavaScript-lastige Seiten)
2. **Extrahieren** – nutzt die Anthropic Claude API, um aus unstrukturiertem Website-Text strukturierte Projektdaten zu ziehen (Projektname, Adresse, Preise, Status, Einheiten)
3. **Speichern** – schreibt in eine SQLite-Datenbank und erkennt automatisch, was sich seit dem letzten Durchlauf geändert hat (Änderungslog)
4. **Präsentieren** – als formatierte Excel-Datei (3 Sheets: Übersicht, Einheiten, Änderungen) **und** als Web-Dashboard im Browser

## Architektur

```
Bauträger-Website
      │
      ▼
crawler.py    → lädt die Website (requests / Playwright)
      │
      ▼
extractor.py  → strukturiert den Text per Claude API zu JSON
      │
      ▼
database.py   → SQLite, erkennt Duplikate & Änderungen über Zeit
      │
      ▼
exporter.py ────────────► Excel-Datei
      │
webapp.py (Flask) ─────► Browser-Dashboard mit Login + Live-Fortschritt
```

`run.py` verbindet Crawler, Extraktor, Datenbank und Export zu einem robusten
Gesamtlauf: Fehler bei einem einzelnen Bauträger (z.B. Website offline) brechen
den Durchlauf nicht ab, sondern werden geloggt, während die übrigen Bauträger
weiter verarbeitet werden.

## Tech-Stack

| Bereich | Werkzeug |
|---|---|
| Web-Scraping | `requests`, `playwright`, `beautifulsoup4` |
| KI-Extraktion | Anthropic Claude API |
| Datenhaltung | SQLite |
| Excel-Export | `openpyxl` |
| Web-UI | Flask, Vanilla JS (Live-Fortschritt per Polling) |
| Deployment | Docker, gunicorn, Render |

## Lokal starten

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env   # eigenen Anthropic API-Key + Passwörter eintragen

# Terminal-Version:
python run.py           # Ergebnis in data/wettbewerb_output.xlsx

# Web-Version:
python webapp.py        # http://127.0.0.1:5001
```

Die Liste der zu crawlenden Bauträger steht in `bautraeger.csv` (Format:
`name;website;stadt;aktiv`) und lässt sich direkt in Excel bearbeiten.

## Hosting

Das Projekt ist container-fertig (`Dockerfile`, `render.yaml`) für ein
Deployment auf Render o.ä., inklusive persistentem Speicher für die
SQLite-Datenbank.

---

*Hinweis: Dies ist eine bereinigte Portfolio-Version. Echte Bauträger-Daten,
API-Keys und Zugangsdaten sind nicht enthalten.*
