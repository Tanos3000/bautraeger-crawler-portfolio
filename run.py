# run.py
# Einstiegspunkt des Crawlers.
# Koordiniert den gesamten Ablauf: Crawler starten → Daten extrahieren → in DB speichern → Excel exportieren.
# Robust: ein Fehler bei einem Bauträger bricht den Gesamtlauf nicht ab.
# Wird so ausgeführt: python run.py

import time
from datetime import datetime

import config
import crawler
import database
import exporter
import extractor


def log(nachricht):
    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    zeile = f"[{zeitstempel}] {nachricht}"
    print(zeile)
    with open(config.PFAD_LOG, "a", encoding="utf-8") as datei:
        datei.write(zeile + "\n")


def haupt(fortschritt_callback=None):
    """fortschritt_callback(dict) wird nach jedem Bauträger aufgerufen, z.B.
    genutzt von webapp.py um den Live-Fortschritt in der UI anzuzeigen.
    Ohne Callback läuft alles wie gewohnt über Terminal + Log-Datei."""
    log("Lauf gestartet")

    database.erstelle_tabellen()
    database.importiere_bautraeger_aus_csv()
    aktive_bautraeger = database.lade_aktive_bautraeger()
    gesamt = len(aktive_bautraeger)

    for index, bautraeger in enumerate(aktive_bautraeger, start=1):
        name = bautraeger["name"]
        url = bautraeger["website"]

        if fortschritt_callback:
            fortschritt_callback({
                "index": index, "gesamt": gesamt, "name": name, "status": "laeuft",
            })

        try:
            html, fehler = crawler.lade_seite(url)
            if fehler:
                raise RuntimeError(f"Seite konnte nicht geladen werden: {fehler}")

            sauberer_text = crawler.bereinige_html(html)
            projekte = extractor.extrahiere_projekte(sauberer_text, url)

            for projekt in projekte:
                database.speichere_projekt(projekt, bautraeger["id"], url)

            database.markiere_gecrawlt(bautraeger["id"])
            log(f"{name}: {len(projekte)} Projekte gefunden. OK")

            if fortschritt_callback:
                fortschritt_callback({
                    "index": index, "gesamt": gesamt, "name": name,
                    "status": "fertig", "projekte": len(projekte),
                })

        except Exception as fehler:
            log(f"{name}: FEHLER - {fehler}")
            if fortschritt_callback:
                fortschritt_callback({
                    "index": index, "gesamt": gesamt, "name": name,
                    "status": "fehler", "fehler": str(fehler),
                })

        time.sleep(config.WARTEZEIT_SEKUNDEN)

    pfad = exporter.erstelle_excel()
    log(f"Lauf beendet. Excel erstellt: {pfad}")

    if fortschritt_callback:
        fortschritt_callback({"status": "abgeschlossen", "excel": pfad})


if __name__ == "__main__":
    haupt()
