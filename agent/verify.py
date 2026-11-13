"""Nachrecherche: schließt Lücken bei den Startup-Kriterien.

Für Startups ohne belegtes Gründungsjahr (oder ohne bisherige Startup-Prüfung)
sucht Claude gezielt nach Gründungsjahr, Beschäftigtenzahl und einem möglichen
Mutterunternehmen. Es gelten dieselben Regeln wie bei der Recherche:
Jede Angabe braucht eine Quelle aus den tatsächlichen Suchergebnissen.
"""
import json

from config import MODEL, MAX_SEARCHES_PER_VERIFY, VERIFY_BATCH_SIZE
from sources import check_fact, normalize_url


def _fact(value_schema):
    return {
        "type": "object",
        "properties": {"value": value_schema, "source": {"type": ["string", "null"]}},
        "required": ["value", "source"],
        "additionalProperties": False,
    }


def _tool(ids):
    return {
        "name": "pruefung_speichern",
        "description": "Speichert die Rechercheergebnisse zu den Startup-Kriterien.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "enum": ids},
                            "founded": _fact({"type": ["integer", "null"]}),
                            "country": _fact({"type": ["string", "null"], "description": "ISO-Ländercode des Hauptsitzes, z. B. DE"}),
                            "employees": _fact({"type": ["integer", "null"]}),
                            "parent_company": _fact({"type": ["string", "null"]}),
                        },
                        "required": ["id", "founded", "country", "employees", "parent_company"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["results"],
            "additionalProperties": False,
        },
    }


SYSTEM_PROMPT = """Du prüfst Unternehmensangaben für eine Startup-Datenbank.
Finde für jedes Unternehmen: Gründungsjahr, Land des Hauptsitzes (ISO-Code), Zahl der Beschäftigten und ob ein anderes Unternehmen (kein Investor) es übernommen hat oder mehrheitlich besitzt.
Regeln: Jede Angabe braucht als "source" eine URL aus deinen Suchergebnissen, die den Wert belegt. Was du nicht belegen kannst, setzt du auf null. Niemals schätzen. Keine Daten über Personen."""


def verify_entries(client, entries):
    """Ergänzt belegte Angaben direkt in den Einträgen. Rückgabe: Anzahl ergänzter Angaben."""
    filled = 0
    for i in range(0, len(entries), VERIFY_BATCH_SIZE):
        batch = entries[i:i + VERIFY_BATCH_SIZE]
        ids = [e["id"] for e in batch]
        listing = [{"id": e["id"], "name": e["name"], "website": e.get("website"),
                    "beschreibung": e["description"]["value"]} for e in batch]
        messages = [{"role": "user", "content":
                     "Prüfe diese Unternehmen:\n" + json.dumps(listing, ensure_ascii=False, indent=1)
                     + "\n\nRufe zum Schluss das Werkzeug pruefung_speichern auf."}]
        seen, result = set(), None
        for _ in range(4):
            response = client.messages.create(
                model=MODEL, max_tokens=4000, system=SYSTEM_PROMPT, messages=messages,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": MAX_SEARCHES_PER_VERIFY},
                       _tool(ids)],
            )
            for block in response.content:
                if block.type == "web_search_tool_result" and isinstance(block.content, list):
                    seen.update(u for u in (normalize_url(getattr(r, "url", None)) for r in block.content) if u)
                elif block.type == "tool_use" and block.name == "pruefung_speichern":
                    result = block.input
            if result is not None:
                break
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "pause_turn":
                messages.append({"role": "user", "content": "Bitte speichere jetzt mit dem Werkzeug pruefung_speichern. Keine weiteren Suchen."})

        by_id = {e["id"]: e for e in batch}
        for r in (result or {}).get("results", []):
            e = by_id.get(r["id"])
            if not e:
                continue
            for key in ("founded", "country", "employees", "parent_company"):
                fact = check_fact(key, r.get(key), seen)
                if fact and (e.get(key) or {}).get("value") is None:
                    e[key] = fact
                    e["sources"] = sorted(set(e.get("sources", [])) | {fact["source"]})
                    filled += 1
                    print(f"  + {e['name']}: {key} = {fact['value']}")
    return filled
