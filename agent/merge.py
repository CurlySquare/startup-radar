"""Abgleichen: erkennt Duplikate und aktualisiert vorhandene Einträge.

Ein Startup gilt als bereits bekannt, wenn die Domain seiner Website ODER
sein bereinigter Name mit einem vorhandenen Eintrag übereinstimmt.
Das ist reiner Code (deterministisch): gleiche Eingabe, gleiches Ergebnis.
"""
import re

from sources import domain_of

FACT_KEYS = ("description", "country", "founded", "funding_stage")
LABELS = {"description": "Beschreibung", "country": "Land", "founded": "Gründungsjahr",
          "funding_stage": "Finanzierungsphase", "website": "Website"}

# Rechtsformen werden beim Namensvergleich ignoriert ("Beispiel GmbH" = "Beispiel")
LEGAL_FORMS = r"\b(gmbh|ag|se|ug|kg|inc|ltd|llc|limited|corp|co|sas|sa|sarl|srl|spa|bv|nv|oy|ab|as|aps|plc)\b\.?"


def normalize_name(name):
    n = name.lower()
    n = re.sub(LEGAL_FORMS, " ", n)
    return re.sub(r"[^a-z0-9]", "", n)


def make_id(entry, existing_ids):
    base = domain_of(entry.get("website")) or normalize_name(entry["name"]) or "startup"
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    candidate, i = base, 2
    while candidate in existing_ids:
        candidate, i = f"{base}-{i}", i + 1
    return candidate


def find_match(entry, startups):
    dom = domain_of(entry.get("website"))
    name = normalize_name(entry["name"])
    for s in startups:
        if dom and dom == domain_of(s.get("website")):
            return s
        if name and name == normalize_name(s["name"]):
            return s
    return None


def merge(db, checked_entries, today):
    """Führt geprüfte Einträge in die Datenbank ein.

    Rückgabe: (neue Einträge, wesentlich geänderte Einträge, nur ergänzte Einträge)

    Wesentlich = neue Finanzierungsphase (echte Neuigkeit, fließt ins Briefing).
    Ergänzt   = bisher leere Angaben werden gefüllt (Datenpflege, kein Briefing).
    Die Beschreibung wird nur ersetzt, wenn bisher keine vorhanden war. Sonst würde
    jede neue Formulierung des Modells als "Änderung" zählen.
    """
    startups = db["startups"]
    new, updated, filled = [], [], []

    for entry in checked_entries:
        match = find_match(entry, startups)

        if match is None:
            entry["id"] = make_id(entry, {s["id"] for s in startups})
            entry["first_seen"] = today
            entry["last_updated"] = today
            entry["history"] = [{"date": today, "change": "Neu aufgenommen"}]
            entry["maturity"] = None
            entry["fit"] = None
            startups.append(entry)
            new.append(entry)
            continue

        changes, material = [], False
        for key in FACT_KEYS:
            new_fact, old = entry[key], match[key]["value"]
            if new_fact["value"] is None or new_fact["value"] == old:
                continue
            if old is None:
                changes.append(f"{LABELS[key]} ergänzt")
                match[key] = new_fact
            elif key == "funding_stage":
                changes.append(f"{LABELS[key]}: {old} → {new_fact['value']}")
                match[key] = new_fact
                material = True
            elif key in ("country", "founded"):
                # Widerspruch zwischen Quellen: alten Wert behalten, aber protokollieren
                changes.append(f"{LABELS[key]}: abweichende Quelle ({new_fact['value']}), bisheriger Wert beibehalten")
        if entry.get("website") and not match.get("website"):
            match["website"] = entry["website"]
            changes.append("Website ergänzt")
        new_sources = set(entry["sources"]) - set(match["sources"])
        match["sources"] = sorted(set(match["sources"]) | set(entry["sources"]))

        if changes or new_sources:
            match["last_updated"] = today
        if changes:
            match["history"].append({"date": today, "change": "; ".join(changes)})
            target = updated if material else filled
            if match not in new and match not in updated and match not in filled:
                target.append(match)
            elif material and match in filled:
                filled.remove(match)
                updated.append(match)

    return new, updated, filled
