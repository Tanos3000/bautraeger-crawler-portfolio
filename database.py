# database.py
# Zuständig für die lokale SQLite-Datenbank.
# Erstellt bei Bedarf die Datenbank und die Tabellen.
# Speichert gecrawlte Projekte und Einheiten, verhindert Duplikate,
# und protokolliert Änderungen im Zeitverlauf (aenderungslog).

import csv
import sqlite3
from datetime import datetime

import config


def verbinde():
    verbindung = sqlite3.connect(config.PFAD_DATENBANK)
    verbindung.execute("PRAGMA foreign_keys = ON")
    return verbindung


def erstelle_tabellen():
    verbindung = verbinde()
    cursor = verbindung.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bautraeger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT NOT NULL UNIQUE,
            stadt TEXT,
            aktiv INTEGER DEFAULT 1,
            zuletzt_gecrawlt TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projekte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bautraeger_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            adresse TEXT,
            anzahl_einheiten INTEGER,
            typ TEXT,
            status TEXT,
            preis_von REAL,
            preis_bis REAL,
            beschreibung TEXT,
            quelle_url TEXT,
            erstmals_gesehen TEXT,
            zuletzt_gesehen TEXT,
            FOREIGN KEY (bautraeger_id) REFERENCES bautraeger (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS einheiten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projekt_id INTEGER NOT NULL,
            typ TEXT,
            zimmer REAL,
            flaeche_m2 REAL,
            preis REAL,
            status TEXT,
            zuletzt_geaendert TEXT,
            FOREIGN KEY (projekt_id) REFERENCES projekte (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aenderungslog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projekt_id INTEGER NOT NULL,
            feld TEXT NOT NULL,
            alter_wert TEXT,
            neuer_wert TEXT,
            datum TEXT,
            FOREIGN KEY (projekt_id) REFERENCES projekte (id)
        )
    """)

    verbindung.commit()
    verbindung.close()


def importiere_bautraeger_aus_csv():
    verbindung = verbinde()
    cursor = verbindung.cursor()

    with open(config.PFAD_BAUTRAEGER, newline="", encoding="utf-8") as datei:
        zeilen = csv.DictReader(datei, delimiter=";")
        for zeile in zeilen:
            cursor.execute(
                "SELECT id FROM bautraeger WHERE website = ?", (zeile["website"],)
            )
            vorhanden = cursor.fetchone()
            if not vorhanden:
                cursor.execute(
                    """INSERT INTO bautraeger (name, website, stadt, aktiv)
                       VALUES (?, ?, ?, ?)""",
                    (
                        zeile["name"],
                        zeile["website"],
                        zeile["stadt"],
                        int(zeile["aktiv"]),
                    ),
                )

    verbindung.commit()
    verbindung.close()


def lade_aktive_bautraeger():
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    cursor.execute("SELECT * FROM bautraeger WHERE aktiv = 1")
    ergebnis = [dict(zeile) for zeile in cursor.fetchall()]
    verbindung.close()
    return ergebnis


def _felder_vergleichen(cursor, projekt_id, alte_zeile, neue_daten, felder):
    heute = datetime.now().isoformat(timespec="seconds")
    for feld in felder:
        alter_wert = alte_zeile[feld]
        neuer_wert = neue_daten.get(feld)
        if neuer_wert is not None and str(neuer_wert) != str(alter_wert):
            cursor.execute(
                """INSERT INTO aenderungslog (projekt_id, feld, alter_wert, neuer_wert, datum)
                   VALUES (?, ?, ?, ?, ?)""",
                (projekt_id, feld, alter_wert, neuer_wert, heute),
            )


def speichere_projekt(projekt_daten, bautraeger_id, quelle_url):
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    heute = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """SELECT * FROM projekte WHERE bautraeger_id = ? AND name = ?""",
        (bautraeger_id, projekt_daten.get("projektname")),
    )
    bestehend = cursor.fetchone()

    vergleichbare_felder = [
        "adresse",
        "anzahl_einheiten",
        "typ",
        "status",
        "preis_von",
        "preis_bis",
        "beschreibung",
    ]
    neue_daten = {
        "adresse": projekt_daten.get("adresse"),
        "anzahl_einheiten": projekt_daten.get("anzahl_einheiten"),
        "typ": projekt_daten.get("typ"),
        "status": projekt_daten.get("status"),
        "preis_von": projekt_daten.get("preis_von"),
        "preis_bis": projekt_daten.get("preis_bis"),
        "beschreibung": projekt_daten.get("beschreibung"),
    }

    if bestehend is None:
        cursor.execute(
            """INSERT INTO projekte
               (bautraeger_id, name, adresse, anzahl_einheiten, typ, status,
                preis_von, preis_bis, beschreibung, quelle_url,
                erstmals_gesehen, zuletzt_gesehen)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                bautraeger_id,
                projekt_daten.get("projektname"),
                neue_daten["adresse"],
                neue_daten["anzahl_einheiten"],
                neue_daten["typ"],
                neue_daten["status"],
                neue_daten["preis_von"],
                neue_daten["preis_bis"],
                neue_daten["beschreibung"],
                quelle_url,
                heute,
                heute,
            ),
        )
        projekt_id = cursor.lastrowid
    else:
        projekt_id = bestehend["id"]
        _felder_vergleichen(cursor, projekt_id, bestehend, neue_daten, vergleichbare_felder)
        cursor.execute(
            """UPDATE projekte SET adresse = ?, anzahl_einheiten = ?, typ = ?,
               status = ?, preis_von = ?, preis_bis = ?, beschreibung = ?,
               zuletzt_gesehen = ? WHERE id = ?""",
            (
                neue_daten["adresse"] if neue_daten["adresse"] is not None else bestehend["adresse"],
                neue_daten["anzahl_einheiten"] if neue_daten["anzahl_einheiten"] is not None else bestehend["anzahl_einheiten"],
                neue_daten["typ"] if neue_daten["typ"] is not None else bestehend["typ"],
                neue_daten["status"] if neue_daten["status"] is not None else bestehend["status"],
                neue_daten["preis_von"] if neue_daten["preis_von"] is not None else bestehend["preis_von"],
                neue_daten["preis_bis"] if neue_daten["preis_bis"] is not None else bestehend["preis_bis"],
                neue_daten["beschreibung"] if neue_daten["beschreibung"] is not None else bestehend["beschreibung"],
                heute,
                projekt_id,
            ),
        )

    verbindung.commit()
    verbindung.close()
    return projekt_id


def speichere_einheit(einheit_daten, projekt_id):
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    heute = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """SELECT * FROM einheiten WHERE projekt_id = ? AND typ = ? AND zimmer = ? AND flaeche_m2 = ?""",
        (
            projekt_id,
            einheit_daten.get("typ"),
            einheit_daten.get("zimmer"),
            einheit_daten.get("flaeche_m2"),
        ),
    )
    bestehend = cursor.fetchone()

    if bestehend is None:
        cursor.execute(
            """INSERT INTO einheiten (projekt_id, typ, zimmer, flaeche_m2, preis, status, zuletzt_geaendert)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                projekt_id,
                einheit_daten.get("typ"),
                einheit_daten.get("zimmer"),
                einheit_daten.get("flaeche_m2"),
                einheit_daten.get("preis"),
                einheit_daten.get("status"),
                heute,
            ),
        )
        einheit_id = cursor.lastrowid
    else:
        einheit_id = bestehend["id"]
        cursor.execute(
            """UPDATE einheiten SET preis = ?, status = ?, zuletzt_geaendert = ? WHERE id = ?""",
            (
                einheit_daten.get("preis", bestehend["preis"]),
                einheit_daten.get("status", bestehend["status"]),
                heute,
                einheit_id,
            ),
        )

    verbindung.commit()
    verbindung.close()
    return einheit_id


def hole_projekte():
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    cursor.execute("""
        SELECT b.name AS bautraeger, p.name AS projekt, p.adresse,
               p.anzahl_einheiten AS einheiten, p.preis_von, p.preis_bis, p.status
        FROM projekte p
        JOIN bautraeger b ON b.id = p.bautraeger_id
        ORDER BY b.name, p.name
    """)
    ergebnis = [dict(zeile) for zeile in cursor.fetchall()]
    verbindung.close()
    return ergebnis


def hole_einheiten():
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    cursor.execute("""
        SELECT p.name AS projekt, e.zimmer, e.flaeche_m2, e.preis, e.status
        FROM einheiten e
        JOIN projekte p ON p.id = e.projekt_id
        ORDER BY p.name
    """)
    ergebnis = []
    for zeile in cursor.fetchall():
        eintrag = dict(zeile)
        eintrag["preis_pro_m2"] = (
            round(eintrag["preis"] / eintrag["flaeche_m2"], 2)
            if eintrag["preis"] and eintrag["flaeche_m2"]
            else None
        )
        ergebnis.append(eintrag)
    verbindung.close()
    return ergebnis


def hole_aenderungen():
    verbindung = verbinde()
    verbindung.row_factory = sqlite3.Row
    cursor = verbindung.cursor()
    cursor.execute("""
        SELECT a.datum, p.name AS projekt, a.feld, a.alter_wert, a.neuer_wert
        FROM aenderungslog a
        JOIN projekte p ON p.id = a.projekt_id
        ORDER BY a.datum DESC
    """)
    ergebnis = [dict(zeile) for zeile in cursor.fetchall()]
    verbindung.close()
    return ergebnis


def markiere_gecrawlt(bautraeger_id):
    verbindung = verbinde()
    cursor = verbindung.cursor()
    heute = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "UPDATE bautraeger SET zuletzt_gecrawlt = ? WHERE id = ?",
        (heute, bautraeger_id),
    )
    verbindung.commit()
    verbindung.close()


if __name__ == "__main__":
    erstelle_tabellen()
    print("Tabellen angelegt.")
    importiere_bautraeger_aus_csv()
    print("Bauträger-Liste importiert.")

    aktive = lade_aktive_bautraeger()
    print(f"\n{len(aktive)} aktive Bauträger in der Datenbank:")
    for eintrag in aktive:
        print(f"  - {eintrag['name']} ({eintrag['website']})")
