# webapp.py
# Browser-Oberfläche für den Bauträger Crawler.
# Zeigt die gespeicherten Daten als Web-Dashboard (Übersicht, Einheiten,
# Änderungen) und erlaubt es, den Crawl per Knopfdruck zu starten - statt
# "python run.py" im Terminal. Passwortgeschützt (gemeinsames Passwort aus
# .env), damit auch Kollegen bei Phoenix Living zugreifen können.
#
# Start: python webapp.py  →  dann im Browser: http://127.0.0.1:5001

import threading
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

import config
import database
import run

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

crawl_status = {
    "laeuft": False,
    "aktuell": None,
    "verlauf": [],
    "letzter_lauf": None,
}
crawl_lock = threading.Lock()


def login_erforderlich(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("eingeloggt"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = None
    if request.method == "POST":
        if request.form.get("passwort") == config.PORTAL_PASSWORT:
            session["eingeloggt"] = True
            return redirect(url_for("dashboard"))
        fehler = "Falsches Passwort."
    return render_template("login.html", fehler=fehler)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_erforderlich
def dashboard():
    return render_template(
        "dashboard.html",
        projekte=database.hole_projekte(),
        einheiten=database.hole_einheiten(),
        aenderungen=database.hole_aenderungen(),
    )


def _fortschritt_aktualisieren(daten):
    if daten.get("status") == "abgeschlossen":
        crawl_status["letzter_lauf"] = daten
        crawl_status["aktuell"] = None
    else:
        crawl_status["aktuell"] = daten
        crawl_status["verlauf"].append(daten)


def _crawl_im_hintergrund():
    try:
        run.haupt(fortschritt_callback=_fortschritt_aktualisieren)
    finally:
        crawl_status["laeuft"] = False
        crawl_status["aktuell"] = None


@app.route("/crawl", methods=["POST"])
@login_erforderlich
def crawl_starten():
    with crawl_lock:
        if crawl_status["laeuft"]:
            return jsonify({"gestartet": False, "info": "Läuft bereits."})
        crawl_status["laeuft"] = True
        crawl_status["verlauf"] = []
        crawl_status["aktuell"] = None
        thread = threading.Thread(target=_crawl_im_hintergrund, daemon=True)
        thread.start()
    return jsonify({"gestartet": True})


@app.route("/status")
@login_erforderlich
def status():
    return jsonify(crawl_status)


# Läuft bei jedem Start - egal ob "python webapp.py" lokal oder gunicorn in
# Produktion (gunicorn importiert nur "app", der "if __name__" Block darunter
# wird dann NICHT ausgeführt).
database.erstelle_tabellen()
database.importiere_bautraeger_aus_csv()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True, use_reloader=False, threaded=True)
