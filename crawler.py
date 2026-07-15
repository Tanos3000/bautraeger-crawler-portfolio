# crawler.py
# Zuständig für das Laden von Webseiten.
# Verwendet requests für einfache HTML-Seiten und Playwright für JavaScript-gerenderte Seiten.
# Gibt den rohen HTML-Inhalt zurück, ohne ihn zu analysieren.

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import config

MINDESTLAENGE = 500  # kürzere Antworten sehen nach leerem JS-Gerüst aus


def lade_seite(url):
    try:
        antwort = requests.get(
            url,
            headers={"User-Agent": config.USER_AGENT},
            timeout=config.TIMEOUT_SEKUNDEN,
        )
        if antwort.ok and len(antwort.text) > MINDESTLAENGE:
            return antwort.text, None
    except requests.RequestException as fehler:
        pass

    try:
        return lade_seite_mit_browser(url), None
    except Exception as fehler:
        return None, str(fehler)


def lade_seite_mit_browser(url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        seite = browser.new_page(user_agent=config.USER_AGENT)
        seite.goto(url, timeout=config.TIMEOUT_SEKUNDEN * 1000)
        html_text = seite.content()
        browser.close()
        return html_text


def bereinige_html(html_text):
    soup = BeautifulSoup(html_text, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    zeilen = [zeile.strip() for zeile in text.splitlines()]
    zeilen = [zeile for zeile in zeilen if zeile]
    return "\n".join(zeilen)


if __name__ == "__main__":
    test_url = "https://www.wohnbaustudio.de/"
    html, fehler = lade_seite(test_url)
    if fehler:
        print(f"Fehler beim Laden: {fehler}")
    else:
        print(f"HTML geladen: {len(html)} Zeichen")
        sauberer_text = bereinige_html(html)
        print(f"Bereinigter Text: {len(sauberer_text)} Zeichen\n")
        print(sauberer_text[:1000])
