# Meilenstein 1 – Grundgerüst

**Datum:** 13.11.2026
**Ergebnis:** Repository, Website-Auslieferung, sicher hinterlegter API-Schlüssel und ein erfolgreicher automatischer Testlauf.

---

## Verwendete Prompts

### Startprompt (wörtlich, an zwei Stellen neutralisiert)

> Ich möchte mit dir ein Portfolio-Projekt umsetzen: den „Startup Radar“, einen KI-Agenten, der auf meiner persönlichen Website (kijanvakilzadeh.com/startup-radar) live zu sehen ist. Führe mich Schritt für Schritt durch den gesamten Prozess.
>
> **Hintergrund**
> Ich bin promovierter Betriebswirt (Strategie, Foresight, Organisationsforschung) und bewerbe mich als (Junior) Manager Innovation & Startups bei **[Zielunternehmen]**. Die Stelle verlangt, ein Startup-Management samt Datenbank aufzubauen, Tech-Trends zu scouten und Agentic-AI-Use-Cases selbst umzusetzen. Der Startup Radar soll genau das im Kleinen zeigen. Ich verlinke ihn im Anschreiben, deshalb muss ein Recruiter in 30 Sekunden verstehen, was er sieht. Meine Vorkenntnisse: Grundlagen in C# und Software-Architektur, wenig Python.
>
> **Was der Agent tun soll**
> - Läuft einmal pro Woche automatisch (z. B. montags).
> - Recherchiert im Web neue oder relevante Startups in diesen Feldern: Retail-Tech/Handel, Logistik & Supply Chain, Kreislaufwirtschaft/Recycling, Food-Tech/Produktion, Cloud/Cyber Security/Data & AI.
> - Erfasst pro Startup: Name, Land, Gründungsjahr, Finanzierungsphase, Kurzbeschreibung, Feld und mindestens eine Quell-URL.
> - Bewertet jedes Startup nach Reifegrad (1–5) und strategischem Fit für einen großen Handels- und Digitalkonzern (1–5), jeweils mit kurzer Begründung.
> - Erkennt Duplikate und aktualisiert vorhandene Einträge, statt sie doppelt anzulegen.
> - Schreibt ein Wochen-Briefing: die Top 5 der Woche plus 2–3 beobachtete Trends.
> - Qualitätsregel: Keine Angabe ohne Quelle. Was nicht belegbar ist, bleibt leer, statt geschätzt zu werden.
>
> **Technik (Vorschlag, prüfe und begründe Alternativen)**
> - Python-Skript mit der Claude API und Websuche (Tool Use)
> - Daten als JSON im GitHub-Repo, automatischer Lauf per GitHub Actions
> - Statisches Frontend (HTML/JS), eingebunden in meine Website. Frag mich zuerst, mit welchem System meine Website läuft, und schlage dann die passende Einbindung vor (Unterseite, Subdomain oder Einbettung).
>
> **Aufbau der Seite**
> 1. Kurzer Einstieg: was der Radar ist und warum ich ihn gebaut habe (neutral, ohne Namen, Logos oder Design **[des Zielunternehmens und seiner Konzernmarken]**)
> 2. Interaktive Startup-Datenbank: Suche, Filter (Feld, Reifegrad, Fit), Sortierung, Quellenlinks
> 3. Aktuelles Wochen-Briefing plus Archiv
> 4. „So funktioniert der Agent“: einfaches Ablaufdiagramm (recherchieren → bewerten → abgleichen → speichern → Briefing)
> 5. „Making-of“: chronologisches Build-Log mit den tatsächlich verwendeten Prompts (inklusive dieses Startprompts), wichtigen Entscheidungen, Problemen und Learnings
> 6. Transparenzhinweis: mit KI-Unterstützung gebaut, Inhalte KI-generiert und nicht vollständig manuell geprüft
>
> Die Seite muss mobil gut funktionieren, schlicht und professionell aussehen und auf Deutsch sein (Englisch optional).
>
> **Sicherheit und sensible Daten**
> - API-Keys gehören nie in Code, Chat oder Making-of, nur in GitHub Secrets. Erinnere mich daran, wenn es so weit ist.
> - Bevor etwas ins Making-of kommt, entferne private Daten (E-Mail, Adresse, Account-Namen, Kosten, Tokens) und zeig mir die bereinigte Fassung.
> - Über Startups nur öffentliche Unternehmensinformationen, keine privaten Daten über Personen.
>
> **Wie wir arbeiten**
> - Beginne mit 2–3 Rückfragen (Website-System, GitHub-Account, Zeitbudget) und schlag dann einen Plan mit Meilensteinen vor.
> - Danach immer nur einen Schritt auf einmal. Warte auf mein „erledigt“, bevor es weitergeht.
> - Erkläre jeden Schritt so, dass ich ihn im Vorstellungsgespräch selbst erklären kann: was passiert und warum diese Entscheidung.
> - Ich arbeite teils am Handy: halte Anweisungen kurz und gib Code als vollständige Dateien, nicht als Schnipsel.
> - Führe das Build-Log laufend mit. Gib mir nach jedem Meilenstein den fertigen Making-of-Eintrag (bereinigt).
> - Zum Schluss: eine Checkliste, ob die Seite recruiter-tauglich ist, und 10 Fragen, die man mir im Gespräch zum Projekt stellen könnte, mit Antwortstichpunkten.

### Folge-Prompts (Auswahl)

> meine website liegt auf GitHub, wird aber von netlify gehostet

> kurze frage, kannst du nicht mit etwaigen Zugängen automatisiert auf GitHub und co schreiben und das alles übernehmen

> erledigt und eingerichtet. Account-name ist: **[entfernt]**

Dazwischen jeweils „erledigt“ als Bestätigung nach jedem Schritt.

---

## Wichtige Entscheidungen

| Entscheidung | Begründung | Verworfene Alternative |
|---|---|---|
| Python + Claude API mit integrierter Websuche | Die Suche liefert Quell-URLs mit. Das ist die Grundlage für die Regel „keine Angabe ohne Quelle“. | C#: möglich, aber mehr Aufwand bei gleichem Ergebnis |
| Daten als JSON im Repository | Kostenlos und versioniert. Die Git-Historie zeigt Woche für Woche, was sich geändert hat. | Externe Datenbank: unnötig für einige hundert Einträge |
| Eigenes Repo, ausgeliefert über GitHub Pages, eingebunden per Netlify-Weiterleitung | Wöchentliche Daten-Updates lösen keine Deploys der Hauptwebsite aus. Das schont das Gratis-Kontingent bei Netlify und hält die Website sauber. | Unterordner im Website-Repo; Subdomain; Einbettung per iframe (schwach auf Mobilgeräten) |
| Trennung `docs/` (Website), `agent/` (Logik), `.github/workflows/` (Automatisierung) | Die Website liest nur Daten. Agent und Darstellung lassen sich unabhängig voneinander ändern. | Alles in einem Ordner |
| Testläufe direkt in GitHub Actions statt lokal | Keine lokale Python-Installation nötig, funktioniert auch vom Handy aus | Lokale Entwicklungsumgebung |
| Claude arbeitet mit eigenem GitHub-Zugriff | Spart Zeit. Der Bau selbst wird zu einem Agentic-AI-Anwendungsfall. | Jede Datei manuell anlegen |
| Zugriff nur auf ausgewählte Repositories | Minimale Rechte (Least Privilege): Der Agent erhält nur, was er braucht. | Zugriff auf alle Repositories |

---

## Probleme und Lösungen

1. **GitHub verbunden, aber Hochladen abgelehnt.** Lesen funktionierte, Schreiben nicht. *Ursache:* Die Verbindung im Chat reicht nicht. Zusätzlich muss die GitHub-App für das Repository installiert sein. *Lösung:* App installiert, freigegeben nur für das Projekt-Repository.
2. **Agent konnte GitHub Pages nicht einschalten.** Diese Einstellung ist für den Agenten gesperrt. *Lösung:* ein manueller Klick. Das ist bewusst so: Einstellungen, die etwas veröffentlichen, bleiben beim Menschen.
3. **Agent konnte die fertige Seite nicht selbst aufrufen.** Seine Internet-Zugriffe sind auf freigegebene Adressen beschränkt. *Lösung:* Sichtprüfung durch mich.

---

## Sicherheit

- Der API-Schlüssel wurde ausschließlich als verschlüsseltes GitHub Secret hinterlegt. Er ist nicht im Code, nicht im Chat und nicht in diesem Log.
- Zusätzlich gilt ein monatliches Ausgabenlimit in der API-Konsole.
- Der Testlauf darf nur lesen und nichts ins Repository schreiben.

---

## Learnings

- **Agentic AI braucht klare Rechte-Grenzen.** Der bauende Agent stieß dreimal an Grenzen: beim Hochladen, bei den Einstellungen und beim Webzugriff. Das war hinderlich, aber richtig so. Die sicherheitsrelevanten Schritte (Schlüssel, Veröffentlichung, Freigaben) bleiben beim Menschen.
- **Erst die ganze Strecke testen, dann Inhalte bauen.** Platzhalterseite und API-Test beweisen, dass Code, Daten, Automatisierung und Auslieferung zusammenspielen, bevor die eigentliche Logik entsteht.
- **Auf die Kosten achten.** Die Wahl des Hostings hing auch davon ab, wie oft Deploys ausgelöst werden.

---

*Bereinigt: Account-Name entfernt; Name des Zielunternehmens und der Konzernmarken neutralisiert. Ebenfalls weggelassen: Kosten, Verbrauchswerte, E-Mail-Adresse und API-Schlüssel.*
