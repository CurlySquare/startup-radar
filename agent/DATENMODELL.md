# Datenmodell und Bewertungsraster

Diese Datei ist die verbindliche Grundlage für den Agenten und die Website.

## Grundregeln

1. **Keine Angabe ohne Quelle.** Jede Faktenangabe (Land, Gründungsjahr, Finanzierungsphase, Beschreibung) hat eine eigene Quell-URL. Ohne Beleg ist der Wert `null`.
2. **Quellen müssen echt sein.** Eine URL zählt nur, wenn sie in den Suchergebnissen des aktuellen Laufs vorkam. Das prüft der Code, nicht das Modell.
3. **Bewertungen sind Einschätzungen, keine Fakten.** Reifegrad und Fit werden als KI-Einschätzung mit Begründung gekennzeichnet.
4. **Keine personenbezogenen Daten.** Keine Namen von Gründer:innen oder Mitarbeitenden, nur öffentliche Unternehmensinformationen.
5. **Nur echte Startups** nach der EU-Empfehlung 2026/720 („innovatives Startup“): jünger als 10 Jahre (Gründungsjahr muss belegt sein), eigenständig (kein Mutterunternehmen; Wagniskapital ist erlaubt), weniger als 100 Beschäftigte und höchstens 10 Mio. € Umsatz, innovatives Angebot. Zusätzlich: **Hauptsitz in Europa** (EU-27, EWR/EFTA inkl. Schweiz, Vereinigtes Königreich), weil der Bezugskonzern auf europäische Souveränität setzt; das Land muss belegt sein. Umsetzung und Grenzen: siehe `agent/eligibility.py`. Wer die Kriterien später nicht mehr erfüllt, wird aus dem Radar entfernt und unter `excluded` mit Grund protokolliert.
6. **Ein Startup = ein Eintrag.** Erkennungsmerkmal ist die Domain der Website (z. B. `beispiel.de`), ersatzweise der bereinigte Name.

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
  "employees":     { "value": 45,         "source": "https://..." },
  "parent_company":{ "value": null,       "source": null },
  "startup_check": { "rule": "EU-Empfehlung 2026/720 (innovatives Startup)", "age": "gegründet 2021",
                     "independent": "keine Hinweise auf ein Mutterunternehmen", "size": "45 Beschäftigte", "passed": true },
  "maturity": { "score": 3, "reason": "Zahlende Kunden im DACH-Raum, Series-A-Finanzierung." },
  "fit":      { "score": 4, "areas": ["logistics", "retail"], "reason": "Optimiert die Filialbelieferung, einen Kernprozess; in einer Region pilotierbar." },
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

**`field`** (Feld). Jedes Feld entspricht einer Sparte des Bezugskonzerns (siehe „Bezugsprofil“):
| Schlüssel | Anzeige | Bezug im Konzern |
|---|---|---|
| `retail` | Retail-Tech / Handel | Lebensmittel-Filialhandel und Online-Marktplatz |
| `food` | Food-Tech / Produktion | Eigenproduktion von Lebensmitteln, Getränken und Verpackungen für die Eigenmarken |
| `circular` | Kreislaufwirtschaft / Recycling | Entsorgung, Sortierung, Recycling und Wertstoffhandel |
| `cloud_ai` | Cloud / Cyber Security / Data & AI | Souveräne europäische Cloud, Cyber Security, Daten und KI |
| `logistics` | Logistik & Supply Chain | Querschnittsfunktion: Warenfluss von Lieferanten und eigenen Werken über Lager zu den Filialen |

**`funding_stage`** (Finanzierungsphase): `Pre-Seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Bootstrapped`, `Öffentlich gefördert`, `Übernommen`, `Börsennotiert`, oder `null` (unbekannt).

**`country`**: zweistelliger Ländercode nach ISO 3166 (z. B. `DE`, `FR`, `US`).

## Bewertungsraster

Feste Stufenbeschreibungen sorgen dafür, dass Bewertungen über Wochen vergleichbar bleiben (verankerte Ratingskalen).

### Reifegrad (1–5)

**Definition:** Der Reifegrad beschreibt, wie weit ein Startup auf dem Weg von der Idee zum etablierten Geschäft ist. Grundlage sind drei belegbare Merkmale: Marktstatus des Produkts, Kundenbasis und Finanzierungsphase. Fehlt ein Merkmal, wird die niedrigere Stufe gewählt. Der Reifegrad sagt nichts über die Erfolgsaussichten aus.

| Stufe | Bezeichnung | Kriterium | Typische Finanzierungsphase |
|---|---|---|---|
| 1 | Idee / Prototyp | Kein Produkt am Markt; Technologie oder Prototyp in Entwicklung | Pre-Seed |
| 2 | Pilotphase | Erstes Produkt, Pilot- oder Testkunden, noch kein belegter regulärer Umsatz | Pre-Seed / Seed |
| 3 | Marktreife | Produkt am Markt mit zahlenden Kunden, frühes Wachstum | Seed / Series A |
| 4 | Skalierung | Mehrere Märkte oder große Referenzkunden, Ausbau von Team und Vertrieb | Series B / C |
| 5 | Etabliert | Breiter Kundenstamm in mehreren Ländern, erprobtes Geschäftsmodell | Series C+ |

### Strategischer Fit (1–5)

**Definition:** Der strategische Fit beschreibt, wie groß der mögliche Nutzen eines Startups für den Bezugskonzern ist. Grundlage sind vier Merkmale: (1) Welche Sparten profitieren? (2) Ist ein Kernprozess betroffen? (3) Ist der Nutzen messbar, etwa bei Kosten, Warenverfügbarkeit, Recyclingquote oder Sicherheit? (4) Lässt sich die Lösung klein pilotieren und auf viele Standorte übertragen? Der Fit sagt nichts über die Qualität des Startups an sich aus.

#### Bezugsprofil

Bewertet wird der Fit für einen großen europäischen Handels- und Digitalkonzern mit fünf Sparten:

1. **Handel:** zwei Lebensmittel-Handelsketten mit über 14.000 Filialen in über 30 Ländern sowie ein Online-Marktplatz
2. **Produktion:** eigene Werke für Lebensmittel, Getränke und Verpackungen der Eigenmarken
3. **Kreislaufwirtschaft:** Entsorgung, Sortierung und Recycling, auch für externe Kunden
4. **Digital:** souveräne europäische Cloud, Cyber Security, KI und IT-Dienste, auch für externe Kunden
5. **Logistik:** Querschnittsfunktion über alle Sparten hinweg

Im Eintrag wird unter `fit.areas` festgehalten, welche Sparten betroffen sind (`retail`, `food`, `circular`, `cloud_ai`, `logistics`).

#### Stufen

| Stufe | Bezeichnung | Kriterium |
|---|---|---|
| 1 | Kein Bezug | Kein Anwendungsfall in einer der fünf Sparten erkennbar |
| 2 | Randbezug | Anwendungsfall nur in einer Unterstützungsfunktion (z. B. Personal, allgemeines Marketing) oder einer Nische, ohne Bezug zu einem Kernprozess |
| 3 | Sparten-Fit | Konkreter Anwendungsfall in genau einer Sparte, z. B. in der Filiale, im Werk, in der Sortieranlage, im Rechenzentrum oder im Lager |
| 4 | Kernprozess-Fit | Adressiert einen Kernprozess einer Sparte mit messbarem Hebel (Kosten, Warenverfügbarkeit, Recyclingquote, Sicherheitsniveau) und ist kurzfristig pilotierbar, z. B. in einzelnen Filialen, Werken oder Ländern |
| 5 | Konzern-Fit | Nutzen in mindestens zwei Sparten oder als gemeinsame Plattform; skalierbar auf tausende Standorte in vielen Ländern; vereinbar mit europäischer Datensouveränität |

#### Prüffragen für die Begründung

- Welche Sparte(n) profitieren, und in welchem Prozess?
- Welcher Hebel ist messbar (Kosten, Verfügbarkeit, Quote, Risiko)?
- Lässt es sich klein pilotieren und dann auf viele Standorte übertragen?
- Gibt es Hürden (z. B. Datenschutz, außereuropäische Datenhaltung, Abhängigkeit von einem Anbieter)?

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
