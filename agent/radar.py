"""Startup Radar – Hauptprogramm.

Ablauf (wird Schritt für Schritt ausgebaut):
  1. recherchieren   (research.py)   ✔
  2. Quellen prüfen  (sources.py)    ✔
  3. bewerten        – folgt
  4. abgleichen      – folgt
  5. speichern       – folgt
  6. Briefing        – folgt

Aufruf:  python agent/radar.py --modus testlauf [--felder retail,food]
Im Testlauf wird nichts in die Datenbank geschrieben, nur nach out/ und ins Protokoll.
"""
import argparse
import json
import os

import anthropic

from config import FIELDS
from research import research_field
from sources import check_startup, domain_of

DATA_FILE = "docs/data/startups.json"


def load_db():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modus", choices=["testlauf"], default="testlauf")
    parser.add_argument("--felder", default="alle", help="z. B. retail,food oder alle")
    args = parser.parse_args()

    fields = list(FIELDS) if args.felder == "alle" else [f.strip() for f in args.felder.split(",")]
    db = load_db()
    known_domains = {domain_of(s.get("website")) for s in db["startups"] if s.get("website")}

    client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
    results, report = [], []

    for field_key in fields:
        print(f"\n=== Feld: {FIELDS[field_key]['label']} ===")
        raw_list, seen_urls, searches = research_field(client, field_key, known_domains)
        kept = 0
        print(f"  Gesehene Ergebnis-URLs: {len(seen_urls)}")
        if os.environ.get("DEBUG") == "true":
            for u in sorted(seen_urls):
                print("    URL:", u)
            print("  Rohdaten:", json.dumps(raw_list, ensure_ascii=False)[:6000])
        for raw in raw_list:
            entry, removed = check_startup(raw, seen_urls, field_key)
            if entry:
                kept += 1
                results.append(entry)
                note = f" (entfernt, da unbelegt: {', '.join(removed)})" if removed else ""
                print(f"  ✔ {entry['name']}{note}")
            else:
                print(f"  ✘ {raw.get('name', '?')} verworfen: keine belegte Beschreibung")
        report.append({"field": field_key, "searches": searches, "found": len(raw_list),
                       "kept": kept, "result_urls": len(seen_urls)})
        print(f"  Suchen: {searches} | gefunden: {len(raw_list)} | übernommen: {kept}")

    os.makedirs("out", exist_ok=True)
    with open("out/recherche.json", "w", encoding="utf-8") as f:
        json.dump({"report": report, "startups": results}, f, ensure_ascii=False, indent=2)

    print("\n=== Zusammenfassung ===")
    for r in report:
        print(f"{r['field']:<10} Suchen {r['searches']}  gefunden {r['found']}  übernommen {r['kept']}")
    print(f"Gesamt übernommen: {len(results)}")


if __name__ == "__main__":
    main()
