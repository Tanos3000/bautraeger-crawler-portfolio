# extractor.py
# Zuständig für das Herausziehen strukturierter Daten aus rohem HTML.
# Verwendet BeautifulSoup (in crawler.py) zum groben Vorputzen, dann die
# Anthropic API für die eigentliche, KI-gestützte Datenextraktion.
# Gibt strukturierte Daten zurück (z.B. Projektname, Anzahl Einheiten, Adresse).

import json

from anthropic import Anthropic

import config

client = Anthropic(api_key=config.API_KEY)

PROJEKT_PROMPT = """Hier ist der Text einer Bauträger-Website (Quelle: {quelle_url}).

Finde alle Neubauprojekte, die auf dieser Seite beschrieben werden. Gib sie als
JSON-Liste zurück. Pro Projekt genau diese Felder:

- projektname (string)
- adresse (string oder null)
- anzahl_einheiten (Zahl oder null)
- typ (string: "Kauf" oder "Miete" oder null)
- preis_von (Zahl in Euro oder null)
- preis_bis (Zahl in Euro oder null)
- status (string, z.B. "Neubau", "im Verkauf", "verkauft" oder null)
- beschreibung (kurzer string oder null)

Wenn ein Feld nicht im Text vorkommt, setze null. Erfinde nichts.
Wenn du keine Projekte findest, gib eine leere Liste [] zurück.
Antworte NUR mit dem JSON, kein Text drumherum, keine Markdown-Codeblöcke.

Text der Website:
{text}
"""


def extrahiere_projekte(sauberer_text, quelle_url):
    prompt = PROJEKT_PROMPT.format(quelle_url=quelle_url, text=sauberer_text)

    try:
        antwort = client.messages.create(
            model=config.CLAUDE_MODELL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        roher_text = antwort.content[0].text.strip()
        roher_text = roher_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        projekte = json.loads(roher_text)
        if not isinstance(projekte, list):
            return []
        return projekte
    except json.JSONDecodeError:
        print(f"  Fehler: Claude-Antwort war kein sauberes JSON ({quelle_url})")
        return []
    except Exception as fehler:
        print(f"  Fehler bei der Extraktion ({quelle_url}): {fehler}")
        return []


if __name__ == "__main__":
    beispieltext = """
    Neubauprojekt "Parkresidenz Killesberg"
    Adresse: Killesbergstraße 12, 70191 Stuttgart
    12 Eigentumswohnungen, Bezug ab Frühjahr 2027.
    Preise ab 480.000 EUR bis 890.000 EUR.
    Status: im Verkauf.
    Moderne Stadtwohnungen mit Blick auf den Killesbergpark.
    """
    ergebnis = extrahiere_projekte(beispieltext, "https://beispiel.de/test")
    print(json.dumps(ergebnis, indent=2, ensure_ascii=False))
