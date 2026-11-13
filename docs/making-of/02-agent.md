# Meilenstein 2 – Der Agent

**Datum:** 13.11.2026
**Ergebnis:** Ein Agent, der jeden Montag automatisch recherchiert, Quellen prüft, Duplikate abgleicht, bewertet, speichert und ein Wochen-Briefing schreibt. Erster Datenbestand: 36 Startups und ein Briefing.

---

## Ablauf des Agenten

```
recherchieren → Quellen prüfen → abgleichen → bewerten → speichern → Briefing
 (Claude +       (Code)          (Code)       (Claude,    (Code)     (Code: Rangfolge,
  Websuche)                                    nach Raster)           Claude: Text)
```

Jeder Schritt ist eine eigene Datei: `research.py`, `sources.py`, `merge.py`, `rate.py`, `briefing.py`. Gesteuert wird alles von `radar.py`.

**Grundprinzip:** Nur die Recherche ist wirklich agentisch, also offen und vom Modell gesteuert. Prüfen, Abgleichen, Rangfolge und Speichern erledigt deterministischer Code.

---

## Verwendete Prompts

### Meine Prompts in diesem Meilenstein

> Fit ist mir sprachlich zu ungenau; der Bezug zur **[Zielunternehmen]** sollte rauskommen. Entsprechend sollten die 5 Felder dies deutlich machen. erledigt

Rückfrage von Claude: Soll der Konzern namentlich genannt werden? Das widerspricht der Neutralitätsregel aus dem Startprompt. Meine Entscheidung: **erkennbar, aber ohne Namen**.

> erledigt; aber warum bauen wir nicht eigentlich nen Agenten bei platform.claude?

> weiter

Dazwischen jeweils „erledigt“.

### Prompt des Agenten (Recherche, Systemanweisung)

> Du bist ein sorgfältiger Startup-Scout für einen großen europäischen Handels- und Digitalkonzern.
>
> Regeln, die immer gelten:
> 1. Keine Angabe ohne Quelle. Jeder Wert braucht als "source" eine URL, die du in deinen Suchergebnissen gesehen hast und die den Wert tatsächlich belegt.
> 2. Was du nicht belegen kannst, setzt du auf null (Wert und Quelle). Niemals schätzen oder aus dem Gedächtnis ergänzen.
> 3. Nur öffentliche Unternehmensinformationen. Keine Namen oder Daten von Personen (auch nicht von Gründer:innen).
> 4. Nur echte Startups: eigenständige junge Unternehmen (in der Regel nach 2012 gegründet), keine Konzerne, Beratungen oder Agenturen.
> 5. Beschreibungen sachlich, auf Deutsch, ohne Werbesprache. Sie sagen konkret, was das Startup anbietet und für wen.
> 6. Nimm ein Startup nur auf, wenn du sein Angebot konkret beschreiben kannst. Keine Platzhalter wie "Details noch nicht belegt".
> 7. Gib immer die offizielle Website an (Startseite, z. B. https://firma.de). Sie ist von Regel 1 ausgenommen, weil das System sie selbst aufruft und prüft. Nur null, wenn du die Adresse wirklich nicht kennst.

Die Prompts für Bewertung und Briefing stehen vollständig im Code (`rate.py`, `briefing.py`). Das Bewertungsraster liest der Agent zur Laufzeit aus `DATENMODELL.md`.

---

## Wichtige Entscheidungen

| Entscheidung | Begründung |
|---|---|
| **Verankerte Bewertungsskalen** (jede Stufe 1–5 mit fester Beschreibung) | Bewertungen bleiben über Wochen vergleichbar. Das Prinzip stammt aus der Organisationsforschung. |
| **Fit-Raster mit fünf Sparten**, erkennbar, aber ohne Namen | Präzise Bewertung bei neutraler Darstellung. Stufe 5 verlangt Nutzen in mindestens zwei Sparten. |
| **Jede Angabe mit eigener Quelle** (`{value, source}`) | Die Belegpflicht steckt in der Datenstruktur selbst. |
| **Quellenprüfung im Code** | Eine URL zählt nur, wenn sie in den tatsächlichen Suchergebnissen vorkam. Das Modell schlägt vor, der Code prüft. |
| **Basisversion der Websuche** | Die Ergebnis-URLs kommen einzeln zurück und lassen sich deshalb prüfen. Neuere Versionen filtern Ergebnisse intern und sind dadurch weniger nachvollziehbar. |
| **Strict Tool Use** | Die API erzwingt das Datenformat. Es reicht nicht, es im Prompt zu erbitten. |
| **Erst abgleichen, dann bewerten** (abweichend vom ursprünglichen Plan) | Bewertet wird der vollständige, zusammengeführte Eintrag. Nur neue oder wesentlich geänderte Startups werden bewertet. |
| **Top 5 nach fester Regel im Code** (Fit → Reifegrad → Anzahl Quellen) | Die Rangfolge ist transparent und reproduzierbar. Claude formuliert nur die Begründungen. |
| **Neuigkeit vs. Datenpflege** | Nur eine neue Finanzierungsphase gilt als Neuigkeit fürs Briefing. Ergänzte Angaben landen nur in der Historie. |
| **Kostenbremsen** | Höchstens 4 Suchen und 5 Startups pro Feld. Zusätzlich gilt das Ausgabenlimit in der API-Konsole. |
| **Claude Managed Agents geprüft, bewusst nicht gewählt** | Managed Agents bieten Zeitplanung und Zugangsdaten-Tresor. Dann prüfte sich aber das Modell selbst, der Agent bräuchte Schreibrechte auf GitHub, und das Produkt ist noch in der Beta. Mögliche Version 2. |

---

## Probleme und Lösungen

1. **Absturz beim ersten Lauf.** Das Modell lieferte Angaben teils als Text statt als Objekt. → Erst habe ich das robustere Einlesen eingebaut, später kam die eigentliche Lösung (siehe 2).
2. **Ganze Felder verworfen.** In manchen Feldern fielen alle Startups durch die Quellenprüfung, in anderen keines. Ein Diagnose-Modus (Rohdaten und Such-URLs im Protokoll) zeigte die Ursache: Das Datenformat war uneinheitlich, dabei gingen Quellen verloren. → Strict Tool Use. Danach wurden 24 von 24 übernommen.
3. **Schema abgelehnt.** Der strikte Modus akzeptiert keine Werteliste mit „leer“ als Typ-Variante. → Umbau auf „Werteliste ODER leer“ (`anyOf`).
4. **Erzwungener Werkzeugaufruf nicht unterstützt.** Das verwendete Modell lehnt `tool_choice` ab. → Die Aufforderung steht jetzt im Prompt, bei Bedarf gibt es einen zweiten Versuch.
5. **Bewertung lieferte nichts.** Bei 24 Startups auf einmal kam keine Bewertung zurück. Unbewertete Einträge wurden (gewollt) nicht veröffentlicht. → Bewertung in Paketen à 8, Abbruchgrund protokollieren, fehlende Einträge nachbewerten.
6. **Scheinbare Änderungen.** Jede neue Formulierung der Beschreibung zählte als Update. Das Briefing war dadurch voller Wiederholungen. → Klare Regel, was eine Neuigkeit ist und was Datenpflege.
7. **Duplikat trotz Prüfung.** „Ultra“ und „Ultra Robotics“ hatten keine Website und unterschiedliche Namen. → Neue Regel: Ein Name beginnt mit dem anderen UND beide teilen eine Quell-URL. Bestehende Duplikate werden bei jedem Lauf automatisch zusammengeführt.
8. **Website fast immer leer.** Die Quellenregel machte das Modell übervorsichtig. → Die Website ist ausdrücklich von der Quellenpflicht ausgenommen, weil der Code sie selbst aufruft.

---

## Sicherheit

- Eingaben beim manuellen Start werden über Umgebungsvariablen übergeben, nicht direkt im Befehl. Das schützt vor eingeschleusten Befehlen.
- Nur der kontrollierte Workflow schreibt ins Repository, der Agent selbst nicht.
- Keine personenbezogenen Daten: Die Regel steht im Prompt und im Datenmodell.

---

## Learnings

- **Die Qualitätsregel hat einen sichtbaren Preis.** Bei vielen Startups fehlt das Gründungsjahr. Das zeige ich offen, statt es mit geschätzten Werten zu füllen.
- **Erst messen, dann reparieren.** Fast jedes Problem wurde erst mit dem Diagnose-Protokoll verständlich.
- **„Agentisch“ ist eine Dosierungsfrage.** So viel Autonomie wie nötig (Recherche), so viel Determinismus wie möglich (Prüfung, Rangfolge, Speichern).
- **Datenqualität ist eine Definitionsfrage.** Was ein Duplikat oder ein Update ist, musste ich fachlich festlegen. Das Modell kann das nicht entscheiden.

---

*Bereinigt: Name des Zielunternehmens neutralisiert. Ebenfalls weggelassen: Account-Name, Kosten, Verbrauchswerte und API-Schlüssel.*
