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

    Rückgabe: (Liste neuer Einträge, Liste aktualisierter Einträge)
    """
    startups = db["startups"]
    new, updated = [], []

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

        changes = []
        for key in FACT_KEYS:
            new_fact = entry[key]
            if new_fact["value"] is not None and new_fact["value"] != match[key]["value"]:
                old = match[key]["value"]
                changes.append(f"{LABELS[key]}: {old if old is not None else '–'} → {new_fact['value']}"
                               if key != "description" else "Beschreibung aktualisiert")
                match[key] = new_fact
        if entry.get("website") and not match.get("website"):
            match["website"] = entry["website"]
            changes.append("Website ergänzt")
        new_sources = set(entry["sources"]) - set(match["sources"])
        match["sources"] = sorted(set(match["sources"]) | set(entry["sources"]))

        if changes:
            match["last_updated"] = today
            match["history"].append({"date": today, "change": "; ".join(changes)})
            if match not in updated and match not in new:
                updated.append(match)
        elif new_sources:
            match["last_updated"] = today

    return new, updated
