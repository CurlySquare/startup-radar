# Startup Radar

Ein KI-Agent, der jede Woche europäische Startups in fünf Zukunftsfeldern des Handels recherchiert, jede Angabe mit einer Quelle belegt und nach Reifegrad und strategischem Fit bewertet.

**Live:** https://kijanvakilzadeh.com/startup-radar/

## Felder
Retail-Tech / Handel · Logistik & Supply Chain · Kreislaufwirtschaft / Recycling · Food-Tech / Produktion · Cloud / Cyber Security / Data & AI

## Ablauf (jeden Montag automatisch)

| Schritt | Wer | Datei |
|---|---|---|
| 1. Recherchieren (wechselndes Unterthema je Feld) | KI + Websuche | `agent/research.py` |
| 2. Quellen prüfen: nur URLs aus echten Suchergebnissen | Code | `agent/sources.py` |
| 3. Startup-Prüfung: EU-Empfehlung 2026/720 + Sitz in Europa, Lücken gezielt nachrecherchieren | Code + KI | `agent/eligibility.py`, `agent/verify.py` |
| 4. Abgleichen: Duplikate, Änderungshistorie | Code | `agent/merge.py` |
| 5. Bewerten: Reifegrad und Fit nach festem Raster | KI | `agent/rate.py` |
| 6. Speichern als JSON im Repository | Code | `docs/data/` |
| 7. Wochen-Briefing: Top 5 per Regel, Trends mit Quellen | Code + KI | `agent/briefing.py` |

Gesteuert von `agent/radar.py`, ausgeführt über GitHub Actions (`.github/workflows/radar.yml`).

## Qualitätsregeln
- Keine Angabe ohne Quelle. Was nicht belegbar ist, bleibt leer.
- Nur Startups nach EU-Definition (jünger als 10 Jahre, eigenständig, unter 100 Beschäftigte) mit Hauptsitz in Europa.
- Nur öffentliche Unternehmensinformationen, keine Daten über Personen.
- Bewertungen sind KI-Einschätzungen mit Begründung, nach dem Raster in [`agent/DATENMODELL.md`](agent/DATENMODELL.md).

## Technik
Python · Claude API (Anthropic) mit Websuche und Strict Tool Use · GitHub Actions · statische Website (HTML/CSS/JS) über GitHub Pages, eingebunden per Netlify-Proxy. Keine Cookies, keine externen Skripte.

## Hinweis
Mit KI-Unterstützung gebaut. Die Inhalte sind KI-generiert und nicht vollständig manuell geprüft.
