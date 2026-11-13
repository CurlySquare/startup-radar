"""Bewerten: Reifegrad und strategischer Fit, jeweils 1–5 mit Begründung.

Grundlage sind ausschließlich die bereits geprüften Fakten (keine neue Suche).
Das Bewertungsraster wird direkt aus agent/DATENMODELL.md gelesen. So gibt es
genau eine Quelle der Wahrheit: Ändert man das Raster dort, bewertet der
Agent beim nächsten Lauf automatisch danach.
"""
import json
import os

from config import MODEL, FIELDS

AREAS = list(FIELDS)  # retail, food, circular, cloud_ai, logistics


def load_rubric():
    path = os.path.join(os.path.dirname(__file__), "DATENMODELL.md")
    text = open(path, encoding="utf-8").read()
    start = text.index("## Bewertungsraster")
    end = text.index("## Ein Briefing-Eintrag")
    return text[start:end].strip()


def _score(desc):
    return {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
            "reason": {"type": "string", "description": desc},
        },
        "required": ["score", "reason"],
        "additionalProperties": False,
    }


RATE_TOOL = {
    "name": "bewertungen_speichern",
    "description": "Speichert die Bewertungen aller übergebenen Startups.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "ratings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "maturity": _score("1–2 Sätze, gestützt auf die übergebenen Fakten"),
                        "fit": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                                "areas": {"type": "array", "items": {"type": "string", "enum": AREAS}},
                                "reason": {"type": "string", "description": "1–2 Sätze: welche Sparte, welcher Prozess, welcher Hebel"},
                            },
                            "required": ["score", "areas", "reason"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["id", "maturity", "fit"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["ratings"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = """Du bewertest Startups für einen großen europäischen Handels- und Digitalkonzern.

Regeln:
1. Bewerte ausschließlich auf Basis der übergebenen Fakten. Nichts ergänzen, nichts aus dem Gedächtnis.
2. Halte dich streng an das Bewertungsraster. Im Zweifel die niedrigere Stufe.
3. Wenn Fakten fehlen (z. B. keine Finanzierungsphase), sag das in der Begründung.
4. Begründungen auf Deutsch, sachlich, 1–2 Sätze, ohne Markennamen des Bezugskonzerns.
5. Bewerte jedes übergebene Startup genau einmal und verwende dessen id."""


def _facts_for_prompt(entry):
    return {
        "id": entry["id"],
        "name": entry["name"],
        "feld": FIELDS[entry["field"]]["label"],
        "beschreibung": entry["description"]["value"],
        "land": entry["country"]["value"],
        "gruendungsjahr": entry["founded"]["value"],
        "finanzierungsphase": entry["funding_stage"]["value"],
    }


def rate_entries(client, entries):
    """Bewertet eine Liste von Einträgen. Rückgabe: {id: {"maturity":..., "fit":...}}."""
    if not entries:
        return {}
    facts = [_facts_for_prompt(e) for e in entries]
    prompt = (
        f"{load_rubric()}\n\n---\n\nBewerte diese {len(facts)} Startups:\n\n"
        + json.dumps(facts, ensure_ascii=False, indent=1)
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=12000,
        system=SYSTEM_PROMPT,
        tools=[RATE_TOOL],
        tool_choice={"type": "tool", "name": RATE_TOOL["name"]},
        messages=[{"role": "user", "content": prompt}],
    )
    ratings = {}
    for block in response.content:
        if block.type == "tool_use":
            for r in block.input.get("ratings", []):
                areas = sorted(set(r["fit"]["areas"]))
                ratings[r["id"]] = {
                    "maturity": {"score": r["maturity"]["score"], "reason": r["maturity"]["reason"]},
                    "fit": {"score": r["fit"]["score"], "areas": areas, "reason": r["fit"]["reason"]},
                }
    return ratings
