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
    # (z. B. Angaben als Objekt, nicht als Text).
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
                        "website": {"type": ["string", "null"], "description": "Offizielle Startseite, z. B. https://firma.de (wird automatisch geprüft, keine Quelle nötig)"},
                        "description": _fact({"type": ["string", "null"], "description": "1–2 Sätze auf Deutsch, max. 220 Zeichen"}),
                        "country": _fact({"type": ["string", "null"], "description": "ISO-Ländercode des Hauptsitzes, z. B. DE"}),
                        "founded": _fact({"type": ["integer", "null"]}),
                        "funding_stage": _fact({"anyOf": [{"type": "string", "enum": FUNDING_STAGES}, {"type": "null"}]}),
                        "employees": _fact({"type": ["integer", "null"], "description": "Zahl der Beschäftigten laut Quelle, sonst null"}),
                        "parent_company": _fact({"type": ["string", "null"], "description": "Unternehmen (kein Investor), das das Startup übernommen hat oder mehrheitlich besitzt; null, wenn es keine Hinweise gibt"}),
                    },
                    "required": ["name", "website", "description", "country", "founded", "funding_stage", "employees", "parent_company"],
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
4. Nur Startups nach der EU-Definition für innovative Startups (Empfehlung 2026/720):
   - weniger als 10 Jahre seit der Gründung,
   - eigenständig: kein Konzern oder anderes Unternehmen als Mutter (Beteiligungen von Wagniskapitalgebern sind erlaubt),
   - weniger als 100 Beschäftigte und höchstens 10 Mio. € Umsatz,
   - mit einem neuen oder deutlich verbesserten Produkt oder Verfahren.
   Keine Konzerne, Tochterfirmen, Beratungen oder Agenturen.
   Zusätzlich: nur Startups mit Hauptsitz in Europa (EU, EWR, Schweiz, Vereinigtes Königreich). Das Land des Hauptsitzes ist Pflicht und muss belegt sein.
   Das Gründungsjahr ist Pflicht: Suche gezielt danach und belege es. Ohne belegtes Gründungsjahr wird ein Startup verworfen.
5. Beschreibungen sachlich, auf Deutsch, ohne Werbesprache. Sie sagen konkret, was das Startup anbietet und für wen.
6. Nimm ein Startup nur auf, wenn du sein Angebot konkret beschreiben kannst. Keine Platzhalter wie "Details noch nicht belegt".
7. Gib immer die offizielle Website an (Startseite, z. B. https://firma.de). Sie ist von Regel 1 ausgenommen, weil das System sie selbst aufruft und prüft. Nur null, wenn du die Adresse wirklich nicht kennst."""


def _user_prompt(field_key, known, today, subtopic):
    field = FIELDS[field_key]
    known = ", ".join(sorted(known)) if known else "keine"
    return f"""Heute ist der {today}.

Recherchiere bis zu {MAX_STARTUPS_PER_FIELD} relevante Startups im Feld "{field['label']}".
Unterthema dieser Suche: {subtopic}.
(Das Feld umfasst allgemein: {field['focus']}.)

Bevorzuge Startups mit aktuellen Meldungen (Finanzierungsrunde, Produktstart, Pilotprojekt mit Händlern oder Herstellern, Auszeichnung) aus den letzten acht Wochen. Nur Startups mit Hauptsitz in Europa.

Bereits bekannt (Namen bzw. Domains): {known}
Suche bevorzugt nach Startups, die hier noch nicht stehen. Bekannte nur aufnehmen, wenn du neue, belegte Informationen gefunden hast.

Erlaubte Finanzierungsphasen: {", ".join(FUNDING_STAGES)}.

Wenn du fertig bist, rufe das Werkzeug "startups_speichern" auf."""


def research_field(client, field_key, known, subtopic):
    """Recherchiert ein Unterthema eines Felds. Rückgabe: (Rohliste, gesehene URLs, Anzahl Suchen)."""
    today = datetime.date.today().isoformat()
    messages = [{"role": "user", "content": _user_prompt(field_key, known, today, subtopic)}]
    seen_urls, searches, result = set(), 0, None

    for _ in range(6):  # Sicherheitsgrenze gegen Endlosschleifen
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            tools=[WEB_SEARCH, SAVE_TOOL],
            messages=messages,
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
        # (Erzwingen per tool_choice unterstützt das Modell nicht, daher als Bitte.)
        messages.append({"role": "user", "content": "Bitte speichere jetzt deine Ergebnisse mit dem Werkzeug startups_speichern. Keine weiteren Suchen."})

    startups = (result or {}).get("startups", [])[:MAX_STARTUPS_PER_FIELD]
    return startups, seen_urls, searches
