"""Startup Radar – Hauptprogramm.

Ablauf:
  1. recherchieren   (research.py)  Websuche pro Feld
  2. Quellen prüfen  (sources.py)   nur belegte Angaben bleiben
  3. abgleichen      (merge.py)     Duplikate erkennen, Einträge aktualisieren
  4. bewerten        (rate.py)      Reifegrad + Fit für neue/geänderte Einträge
  5. speichern                      docs/data/startups.json
  6. Briefing        (briefing.py)  Top 5 + Trends der Woche

Aufruf:
  python agent/radar.py --modus testlauf      (nichts wird gespeichert)
  python agent/radar.py --modus vollstaendig  (Datenbank wird aktualisiert)
"""
import argparse
import datetime
import json
import os

import anthropic

from briefing import make_briefing
from config import FIELDS
from merge import dedupe_existing, merge
from rate import rate_entries
from research import research_field
from sources import check_startup, domain_of

DATA_FILE = "docs/data/startups.json"
BRIEFING_FILE = "docs/data/briefings.json"


def load_db():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modus", choices=["testlauf", "vollstaendig"], default="testlauf")
    parser.add_argument("--felder", default="alle", help="z. B. retail,food oder alle")
    args = parser.parse_args()

    today = datetime.date.today().isoformat()
    fields = list(FIELDS) if args.felder == "alle" else [f.strip() for f in args.felder.split(",")]
    db = load_db()
    for m in dedupe_existing(db, today):
        print(f"Bestehendes Duplikat zusammengeführt: {m}")
    known_domains = {domain_of(s.get("website")) for s in db["startups"] if s.get("website")}
    client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung

    # --- 1 + 2: recherchieren und Quellen prüfen ---
    checked, report = [], []
    for field_key in fields:
        print(f"\n=== Feld: {FIELDS[field_key]['label']} ===")
        raw_list, seen_urls, searches = research_field(client, field_key, known_domains)
        print(f"  Gesehene Ergebnis-URLs: {len(seen_urls)}")
        if os.environ.get("DEBUG") == "true":
            for u in sorted(seen_urls):
                print("    URL:", u)
            print("  Rohdaten:", json.dumps(raw_list, ensure_ascii=False)[:6000])
        kept = 0
        for raw in raw_list:
            entry, removed = check_startup(raw, seen_urls, field_key)
            if entry:
                kept += 1
                checked.append(entry)
                note = f" (entfernt, da unbelegt: {', '.join(removed)})" if removed else ""
                print(f"  ✔ {entry['name']}{note}")
            else:
                name = raw.get("name", "?") if isinstance(raw, dict) else "?"
                print(f"  ✘ {name} verworfen: keine belegte Beschreibung; {'; '.join(removed)}")
        report.append({"field": field_key, "searches": searches, "found": len(raw_list), "kept": kept})

    # --- 3: abgleichen ---
    new, updated, filled = merge(db, checked, today)
    print(f"\n=== Abgleich ===\n  neu: {len(new)} | neue Finanzierungsphase: {len(updated)} | "
          f"Angaben ergänzt: {len(filled)} | "
          f"ohne Änderung: {len(checked) - len(new) - len(updated) - len(filled)}")

    # --- 4: bewerten (neue Einträge und solche mit neuer Finanzierungsphase) ---
    print("\n=== Bewertung ===")
    to_rate = new + updated
    ratings = rate_entries(client, to_rate)
    for e in to_rate:
        r = ratings.get(e["id"])
        if not r:
            print(f"  ! Keine Bewertung erhalten für {e['name']}")
            continue
        old_fit = (e.get("fit") or {}).get("score")
        old_mat = (e.get("maturity") or {}).get("score")
        e["maturity"], e["fit"] = r["maturity"], r["fit"]
        if e in updated and (old_fit, old_mat) != (r["fit"]["score"], r["maturity"]["score"]):
            e["history"].append({"date": today, "change":
                f"Bewertung: Reifegrad {old_mat} → {r['maturity']['score']}, Fit {old_fit} → {r['fit']['score']}"})
        print(f"  {e['name']:<28} Reifegrad {r['maturity']['score']}  Fit {r['fit']['score']}  {r['fit']['areas']}")

    # Einträge, die (z. B. wegen eines Fehlers) keine Bewertung haben, nicht veröffentlichen
    db["startups"] = [s for s in db["startups"] if s.get("fit") and s.get("maturity")]

    # --- 5: speichern ---
    db["updated"] = today
    week_entries = [e for e in new + updated if e.get("fit")]
    db["last_run"] = {"date": today, "new": [e["id"] for e in new if e.get("fit")],
                      "updated": [e["id"] for e in updated], "filled": [e["id"] for e in filled],
                      "report": report}

    # --- 6: Briefing ---
    print("\n=== Briefing ===")
    briefing = make_briefing(client, week_entries, len(db["startups"]), today)
    if briefing:
        names = {s["id"]: s["name"] for s in db["startups"]}
        for i, t in enumerate(briefing["top5"], 1):
            print(f"  {i}. {names[t['id']]}: {t['why']}")
        for t in briefing["trends"]:
            print(f"  Trend: {t['title']}")
    else:
        print("  Keine neuen oder geänderten Startups – kein Briefing.")

    if args.modus == "vollstaendig":
        save_json(DATA_FILE, db)
        if briefing:
            with open(BRIEFING_FILE, encoding="utf-8") as f:
                archive = json.load(f)
            # Bei mehreren Läufen am selben Tag gilt der letzte
            archive["briefings"] = [briefing] + [b for b in archive["briefings"] if b["date"] != today]
            save_json(BRIEFING_FILE, archive)
        print(f"\nGespeichert: {len(db['startups'])} Startups, Briefing: {'ja' if briefing else 'nein'}")
    else:
        print("\nTestlauf: nichts gespeichert.")
        os.makedirs("out", exist_ok=True)
        save_json("out/vorschau.json", {"startups": db, "briefing": briefing})

if __name__ == "__main__":
    main()
