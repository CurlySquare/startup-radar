"""Startup-Prüfung nach der EU-Empfehlung 2026/720 ("innovatives Startup").

Kriterien der EU (alle müssen erfüllt sein):
  1. Alter:      weniger als 10 Jahre seit der Registrierung
  2. Eigenständig: kein Unternehmen hält die Mehrheit bzw. kontrolliert es
                 (Beteiligungen von Wagniskapitalgebern, Business Angels, Hochschulen sind erlaubt)
  3. Größe:      weniger als 100 Beschäftigte; Umsatz oder Bilanzsumme höchstens 10 Mio. €
  4. Innovativ:  neues oder deutlich verbessertes Produkt bzw. Verfahren

Zusätzliche Regel des Radars:
  5. Sitz:       Hauptsitz in Europa (EU-27, EWR/EFTA, Vereinigtes Königreich),
                 weil der Bezugskonzern auf europäische Souveränität setzt.

Umsetzung im Radar (öffentliche Quellen sind begrenzt, daher klar geregelt):
  - Sitz:        Land MUSS belegt sein; außerhalb Europas -> nicht aufgenommen.
  - Alter:       Gründungsjahr MUSS belegt sein, sonst nicht aufgenommen.
  - Eigenständig: Ausschluss bei belegtem Mutterunternehmen oder Finanzierungsphase "Übernommen".
  - Größe:       Ausschluss bei belegten 100+ Beschäftigten. Umsatz wird selten veröffentlicht;
                 er wird daher nicht geprüft, die Angabe lautet dann "keine Hinweise".
  - Innovativ:   über die Recherche-Regeln und die Beschreibung abgedeckt.
"""
import datetime

from config import EUROPE_COUNTRIES, STARTUP_MAX_AGE_YEARS, STARTUP_MAX_EMPLOYEES

RULE = "EU-Empfehlung 2026/720 (innovatives Startup)"


def check_eligibility(entry, today):
    """Rückgabe: (geeignet?, harter Ausschluss?, Prüfprotokoll)."""
    year = datetime.date.fromisoformat(today).year
    founded = (entry.get("founded") or {}).get("value")
    employees = (entry.get("employees") or {}).get("value")
    parent = (entry.get("parent_company") or {}).get("value")
    stage = (entry.get("funding_stage") or {}).get("value")
    country = (entry.get("country") or {}).get("value")

    result = {"rule": RULE, "checked": today}
    ok, hard = True, False

    # 1. Alter
    if founded is None:
        result["age"] = "Gründungsjahr nicht belegt"
        ok = False  # weicher Ausschluss: kann bei späterer Recherche nachgeholt werden
    elif year - founded >= STARTUP_MAX_AGE_YEARS:
        result["age"] = f"gegründet {founded}, älter als {STARTUP_MAX_AGE_YEARS} Jahre"
        ok, hard = False, True
    else:
        result["age"] = f"gegründet {founded}"

    # 2. Eigenständigkeit
    if parent:
        result["independent"] = f"gehört zu {parent}"
        ok, hard = False, True
    elif stage == "Übernommen":
        result["independent"] = "übernommen"
        ok, hard = False, True
    else:
        result["independent"] = "keine Hinweise auf ein Mutterunternehmen"

    # Sitz in Europa
    if country is None:
        result["region"] = "Sitz nicht belegt"
        ok = False  # weicher Ausschluss
    elif country not in EUROPE_COUNTRIES:
        result["region"] = f"Sitz außerhalb Europas ({country})"
        ok, hard = False, True
    else:
        result["region"] = f"Sitz in Europa ({country})"

    # 3. Größe
    if employees is not None and employees >= STARTUP_MAX_EMPLOYEES:
        result["size"] = f"{employees} Beschäftigte"
        ok, hard = False, True
    elif employees is not None:
        result["size"] = f"{employees} Beschäftigte"
    else:
        result["size"] = f"keine Hinweise auf {STARTUP_MAX_EMPLOYEES} oder mehr Beschäftigte"

    result["passed"] = ok
    return ok, hard, result
