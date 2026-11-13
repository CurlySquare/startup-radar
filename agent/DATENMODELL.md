# Datenmodell und Bewertungsraster

Diese Datei ist die verbindliche Grundlage für den Agenten und die Website.

## Grundregeln

1. **Keine Angabe ohne Quelle.** Jede Faktenangabe (Land, Gründungsjahr, Finanzierungsphase, Beschreibung) hat eine eigene Quell-URL. Ohne Beleg ist der Wert `null`.
2. **Quellen müssen echt sein.** Eine URL zählt nur, wenn sie in den Suchergebnissen des aktuellen Laufs vorkam. Das prüft der Code, nicht das Modell.
3. **Bewertungen sind Einschätzungen, keine Fakten.** Reifegrad und Fit werden als KI-Einschätzung mit Begründung gekennzeichnet.
4. **Keine personenbezogenen Daten.** Keine Namen von Gründer:innen oder Mitarbeitenden, nur öffentliche Unternehmensinformationen.
5. **Ein Startup = ein Eintrag.** Erkennungsmerkmal ist die Domain der Website (z. B. `beispiel.de`), ersatzweise der bereinigte Name.

## Dateien

| Datei | Inhalt |
|---|---|
| `docs/data/startups.json` | Die Startup-Datenbank |
| `docs/data/briefings.json` | Alle Wochen-Briefings, neuestes zuerst |

## Ein Startup-Eintrag

```json
{
  "id": "beispiel-de",
  "name": "Beispiel GmbH",
  "website": "https://beispiel.de",
  "field": "logistics",
  "description":   { "value": "Software zur Routenoptimierung für Filialbelieferung.", "source": "https://..." },
  "country":       { "value": "DE",       "source": "https://..." },
  "founded":       { "value": 2021,       "source": "https://..." },
  "funding_stage": { "value": "Series A", "source": "https://..." },
  "maturity": { "score": 3, "reason": "Zahlende Kunden im DACH-Raum, Series-A-Finanzierung." },
  "fit":      { "score": 4, "reason": "Adressiert Filialbelieferung, ein Kernprozess im Handel." },
  "sources": ["https://...", "https://..."],
  "first_seen": "2026-11-16",
  "last_updated": "2026-11-16",
  "history": [
    { "date": "2026-11-16", "change": "Neu aufgenommen" }
  ]
}
```
*(Fiktives Beispiel zur Veranschaulichung.)*

### Feste Wertelisten

**`field`** (Feld):
| Schlüssel | Anzeige |
|---|---|
| `retail` | Retail-Tech / Handel |
| `logistics` | Logistik & Supply Chain |
| `circular` | Kreislaufwirtschaft / Recycling |
| `food` | Food-Tech / Produktion |
| `cloud_ai` | Cloud / Cyber Security / Data & AI |

**`funding_stage`** (Finanzierungsphase): `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Bootstrapped`, `Öffentlich gefördert`, `Übernommen`, `Börsennotiert`, oder `null` (unbekannt).

**`country`**: zweistelliger Ländercode nach ISO 3166 (z. B. `DE`, `FR`, `US`).

## Bewertungsraster

Feste Stufenbeschreibungen sorgen dafür, dass Bewertungen über Wochen vergleichbar bleiben (verankerte Ratingskalen).

### Reifegrad (1–5)

| Stufe | Beschreibung |
|---|---|
| 1 | Idee oder Prototyp, noch kein Produkt am Markt |
| 2 | Erstes Produkt, Pilotkunden oder Testbetrieb |
| 3 | Produkt am Markt mit zahlenden Kunden, frühes Wachstum |
| 4 | Skalierung: mehrere Märkte oder große Kunden, deutliche Finanzierung |
| 5 | Etabliert: breiter Kundenstamm, späte Phase, übernommen oder börsennotiert |

### Strategischer Fit (1–5)

Bezugspunkt: ein großer europäischer Handels- und Digitalkonzern mit Lebensmittelhandel, eigener Produktion, Logistik, Entsorgung/Recycling sowie Cloud- und Security-Geschäft.

| Stufe | Beschreibung |
|---|---|
| 1 | Kein erkennbarer Bezug zu den Geschäftsfeldern |
| 2 | Indirekter Bezug oder Nischenanwendung |
| 3 | Klarer Anwendungsfall in einem Geschäftsbereich |
| 4 | Löst ein relevantes Problem in einem Kernprozess (z. B. Filiale, Lager, Lieferkette, Rücknahme), pilotfähig |
| 5 | Hebelwirkung über mehrere Bereiche, auf Konzernebene skalierbar, passt zu europäischen Anforderungen (z. B. Datenschutz, Datensouveränität) |

## Ein Briefing-Eintrag

```json
{
  "date": "2026-11-16",
  "top5": [
    { "id": "beispiel-de", "why": "Warum diese Woche relevant (1–2 Sätze)." }
  ],
  "trends": [
    { "title": "Kurzer Trendtitel", "text": "2–3 Sätze.", "sources": ["https://..."] }
  ],
  "stats": { "new": 8, "updated": 3, "total": 42 }
}
```
