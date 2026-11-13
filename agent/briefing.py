"""Briefing: Top 5 der Woche plus 2–3 beobachtete Trends.

Die Rangfolge der Top 5 berechnet der Code nach einer festen Regel:
  1. höchster Fit, 2. höchster Reifegrad, 3. meiste Quellen.
Claude schreibt nur die Begründungen ("Warum relevant?") und erkennt Trends.
Jeder Trend braucht mindestens eine Quelle aus den Daten dieser Woche,
sonst wird er verworfen (Regel: keine Angabe ohne Quelle).
"""
import datetime
import json

from config import MODEL, FIELDS
from sources import normalize_url

SYSTEM_PROMPT = """Du schreibst das wöchentliche Startup-Briefing für das Innovationsteam eines großen europäischen Handels- und Digitalkonzerns.

Regeln:
1. Nutze ausschließlich die übergebenen Daten. Nichts ergänzen, nichts aus dem Gedächtnis.
2. Deutsch, sachlich, knapp. Keine Werbesprache, keine Markennamen des Bezugskonzerns.
3. Trends: Muster, die sich über mehrere Startups dieser Woche zeigen (nicht ein einzelnes Startup). Jeder Trend nennt 1–3 Quell-URLs aus den übergebenen Daten."""


def rank(entries):
    return sorted(entries, key=lambda e: (-e["fit"]["score"], -e["maturity"]["score"], -len(e["sources"])))


def _tool(top_ids):
    return {
        "name": "briefing_speichern",
        "description": "Speichert das Wochen-Briefing.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "top5": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "enum": top_ids},
                            "why": {"type": "string", "description": "1–2 Sätze: warum diese Woche relevant"},
                        },
                        "required": ["id", "why"],
                        "additionalProperties": False,
                    },
                },
                "trends": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "max. 6 Wörter"},
                            "text": {"type": "string", "description": "2–3 Sätze"},
                            "sources": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["title", "text", "sources"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["top5", "trends"],
            "additionalProperties": False,
        },
    }


def _brief(e):
    return {
        "id": e["id"], "name": e["name"], "feld": FIELDS[e["field"]]["label"],
        "beschreibung": e["description"]["value"], "land": e["country"]["value"],
        "finanzierungsphase": e["funding_stage"]["value"],
        "reifegrad": e["maturity"], "fit": e["fit"],
        "aenderung": e["history"][-1]["change"], "quellen": e["sources"],
    }


def make_briefing(client, week_entries, total, today):
    """Erstellt das Briefing. Rückgabe: Briefing-Objekt oder None (nichts Neues)."""
    week_entries = [e for e in week_entries if e.get("fit") and e.get("maturity")]
    if not week_entries:
        return None

    ranked = rank(week_entries)
    top = ranked[:5]
    top_ids = [e["id"] for e in top]
    allowed_sources = {normalize_url(u): u for e in week_entries for u in e["sources"]}

    prompt = (
        f"Heute ist der {today}.\n\n"
        f"Top 5 der Woche (Reihenfolge steht fest, bitte beibehalten):\n"
        f"{json.dumps([_brief(e) for e in top], ensure_ascii=False, indent=1)}\n\n"
        f"Alle neuen oder aktualisierten Startups dieser Woche (für die Trends):\n"
        f"{json.dumps([_brief(e) for e in week_entries], ensure_ascii=False, indent=1)}\n\n"
        f"Schreibe zu jedem der Top 5 eine Begründung und beschreibe 2–3 Trends. "
        f"Rufe zum Schluss das Werkzeug briefing_speichern auf."
    )
    tool = _tool(top_ids)
    messages = [{"role": "user", "content": prompt}]
    result = None
    for _ in range(2):
        response = client.messages.create(model=MODEL, max_tokens=6000, system=SYSTEM_PROMPT,
                                          tools=[tool], messages=messages)
        result = next((b.input for b in response.content if b.type == "tool_use"), None)
        if result:
            break
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": "Bitte speichere das Briefing jetzt mit dem Werkzeug briefing_speichern."})
    if not result:
        raise RuntimeError("Briefing konnte nicht erstellt werden.")

    # Reihenfolge der Top 5 kommt aus dem Code, nicht vom Modell
    why = {t["id"]: t["why"] for t in result["top5"]}
    top5 = [{"id": i, "why": why.get(i, "")} for i in top_ids]

    # Trends nur mit belegten Quellen behalten
    trends = []
    for t in result["trends"]:
        srcs = [allowed_sources[normalize_url(u)] for u in t["sources"] if normalize_url(u) in allowed_sources]
        if srcs:
            trends.append({"title": t["title"], "text": t["text"], "sources": srcs[:3]})
        else:
            print(f"  Trend verworfen (keine belegte Quelle): {t['title']}")
    trends = trends[:3]

    year, week, _ = datetime.date.fromisoformat(today).isocalendar()
    return {
        "date": today,
        "week": f"KW {week}/{year}",
        "top5": top5,
        "trends": trends,
        "stats": {"new": sum(1 for e in week_entries if e["first_seen"] == today),
                  "updated": sum(1 for e in week_entries if e["first_seen"] != today),
                  "total": total},
    }
