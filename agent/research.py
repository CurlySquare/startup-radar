"""Schritt 1 des Agenten: Recherchieren.

Pro Feld bekommt Claude die Websuche als Werkzeug und sucht nach aktuellen
Startups. Am Ende muss Claude das Werkzeug "startups_speichern" aufrufen.
Dessen Eingabeformat ist fest vorgegeben (JSON-Schema), so kommen die Daten
immer in derselben Struktur zurück.
"""
import datetime

from config import MODEL, FIELDS, FUNDING_STAGES, MAX_SEARCHES_PER_FIELD, MAX_STARTUPS_PER_FIELD
from sources import normalize_url


def _fact(value_schema):
    return {
        "type": "object",
        "properties": {
            "value": value_schema,
            "source": {"type": ["string", "null"], "description": "URL aus den Suchergebnissen, die den Wert belegt"},
        },
        "required": ["value", "source"],
        "additionalProperties": False,
    }


WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": MAX_SEARCHES_PER_FIELD}

SAVE_TOOL = {
    "name": "startups_speichern",
    "description": "Speichert die recherchierten Startups. Rufe dieses Werkzeug genau einmal am Ende auf.",
    # strict: Die API garantiert, dass die Eingabe exakt dem Schema entspricht
    # (z. B. Angaben als Objekt, nicht als Text). Siehe Making-of: Problem "verschluckte Quellen".
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "startups": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "website": {"type": ["string", "null"], "description": "Offizielle Website des Startups"},
                        "description": _fact({"type": ["string", "null"], "description": "1–2 Sätze auf Deutsch, max. 220 Zeichen"}),
                        "country": _fact({"type": ["string", "null"], "description": "ISO-Ländercode des Hauptsitzes, z. B. DE"}),
                        "founded": _fact({"type": ["integer", "null"]}),
                        "funding_stage": _fact({"type": ["string", "null"], "enum": FUNDING_STAGES + [None]}),
                    },
                    "required": ["name", "website", "description", "country", "founded", "funding_stage"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["startups"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = """Du bist ein sorgfältiger Startup-Scout für einen großen europäischen Handels- und Digitalkonzern.

Regeln, die immer gelten:
1. Keine Angabe ohne Quelle. Jeder Wert braucht als "source" eine URL, die du in deinen Suchergebnissen gesehen hast und die den Wert tatsächlich belegt.
2. Was du nicht belegen kannst, setzt du auf null (Wert und Quelle). Niemals schätzen oder aus dem Gedächtnis ergänzen.
3. Nur öffentliche Unternehmensinformationen. Keine Namen oder Daten von Personen (auch nicht von Gründer:innen).
4. Nur echte Startups: eigenständige junge Unternehmen (in der Regel nach 2012 gegründet), keine Konzerne, Beratungen oder Agenturen.
5. Beschreibungen sachlich, auf Deutsch, ohne Werbesprache. Sie sagen konkret, was das Startup anbietet und für wen.
6. Nimm ein Startup nur auf, wenn du sein Angebot konkret beschreiben kannst. Keine Platzhalter wie "Details noch nicht belegt".
7. Gib die offizielle Website an (Startseite, z. B. https://firma.de), wenn sie in Pressemitteilungen oder Suchergebnissen genannt wird. Sie wird automatisch auf Erreichbarkeit geprüft."""


def _user_prompt(field_key, known_domains, today):
    field = FIELDS[field_key]
    known = ", ".join(sorted(known_domains)) if known_domains else "keine"
    return f"""Heute ist der {today}.

Recherchiere bis zu {MAX_STARTUPS_PER_FIELD} relevante Startups im Feld "{field['label']}".
Schwerpunkt: {field['focus']}.

Bevorzuge Startups mit aktuellen Meldungen (Finanzierungsrunde, Produktstart, Pilotprojekt mit Händlern oder Herstellern, Auszeichnung) aus den letzten acht Wochen. Europa hat Vorrang, weltweit ist erlaubt.

Bereits in der Datenbank (Domains): {known}
Diese nur aufnehmen, wenn du neue, belegte Informationen gefunden hast.

Erlaubte Finanzierungsphasen: {", ".join(FUNDING_STAGES)}.

Wenn du fertig bist, rufe das Werkzeug "startups_speichern" auf."""


def research_field(client, field_key, known_domains):
    """Recherchiert ein Feld. Rückgabe: (Rohliste, gesehene URLs, Anzahl Suchen)."""
    today = datetime.date.today().isoformat()
    messages = [{"role": "user", "content": _user_prompt(field_key, known_domains, today)}]
    seen_urls, searches, result = set(), 0, None
    force_save = False

    for _ in range(6):  # Sicherheitsgrenze gegen Endlosschleifen
        kwargs = {}
        if force_save:
            kwargs["tool_choice"] = {"type": "tool", "name": SAVE_TOOL["name"]}
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            tools=[WEB_SEARCH, SAVE_TOOL],
            messages=messages,
            **kwargs,
        )

        for block in response.content:
            if block.type == "server_tool_use":
                searches += 1
            elif block.type == "web_search_tool_result" and isinstance(block.content, list):
                for item in block.content:
                    url = normalize_url(getattr(item, "url", None))
                    if url:
                        seen_urls.add(url)
            elif block.type == "tool_use" and block.name == SAVE_TOOL["name"]:
                result = block.input

        if result is not None:
            break

        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "pause_turn":
            continue  # lange Suche wurde pausiert: einfach fortsetzen
        # Claude hat geantwortet, ohne zu speichern: freundlich zum Speichern auffordern
        messages.append({"role": "user", "content": "Bitte speichere jetzt deine Ergebnisse mit dem Werkzeug startups_speichern."})
        force_save = True

    startups = (result or {}).get("startups", [])[:MAX_STARTUPS_PER_FIELD]
    return startups, seen_urls, searches
