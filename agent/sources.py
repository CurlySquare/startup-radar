"""Quellenprüfung: setzt die Regel "Keine Angabe ohne Quelle" im Code durch.

Das Sprachmodell darf Quellen vorschlagen. Ob eine Quelle zählt, entscheidet
aber dieser Code: Die URL muss in den Suchergebnissen des aktuellen Laufs
vorgekommen sein. Erfundene oder falsch abgeschriebene Links fallen so heraus.
"""
import datetime
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import requests

from config import FUNDING_STAGES


def normalize_url(url):
    """Vereinheitlicht eine URL, damit gleiche Links als gleich erkannt werden.

    Entfernt z. B. "www.", Tracking-Parameter (utm_...), Sprungmarken (#...)
    und den Schrägstrich am Ende.
    """
    if not url or not isinstance(url, str):
        return None
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    host = parts.netloc.lower().removeprefix("www.")
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith("utm_")])
    path = parts.path.rstrip("/")
    return urlunsplit(("https", host, path, query, ""))


def domain_of(url):
    """Liefert die Domain einer URL ohne "www.", z. B. "beispiel.de"."""
    norm = normalize_url(url)
    return urlsplit(norm).netloc if norm else None


def website_reachable(url):
    """Prüft, ob die angegebene Firmenwebsite tatsächlich existiert."""
    try:
        r = requests.get(url, timeout=10, allow_redirects=True, stream=True,
                         headers={"User-Agent": "Mozilla/5.0 (StartupRadar; Quellenpruefung)"})
        r.close()
        # 403 heißt meist "Bots unerwünscht" – die Seite existiert trotzdem.
        return r.status_code < 500 and r.status_code not in (404, 410)
    except requests.RequestException:
        return False


def _fact_ok(key, value):
    """Prüft, ob ein Wert zum Datenmodell passt (feste Wertelisten, Formate)."""
    if value in (None, ""):
        return False
    if key == "country":
        return isinstance(value, str) and re.fullmatch(r"[A-Z]{2}", value) is not None
    if key == "founded":
        return isinstance(value, int) and 1990 <= value <= datetime.date.today().year
    if key == "funding_stage":
        return value in FUNDING_STAGES
    if key == "description":
        return isinstance(value, str) and len(value) >= 20
    return True


def check_startup(raw, seen_urls, field_key):
    """Prüft einen vom Modell gelieferten Eintrag.

    Rückgabe: (geprüfter Eintrag oder None, Protokoll der entfernten Angaben)
    """
    removed = []
    name = (raw.get("name") or "").strip()
    entry = {"name": name, "field": field_key}

    for key in ("description", "country", "founded", "funding_stage"):
        fact = raw.get(key) or {}
        value, source = fact.get("value"), fact.get("source")
        if _fact_ok(key, value) and normalize_url(source) in seen_urls:
            entry[key] = {"value": value, "source": source}
        else:
            entry[key] = {"value": None, "source": None}
            if value not in (None, ""):
                removed.append(key)

    website = normalize_url(raw.get("website"))
    if website and website_reachable(website):
        entry["website"] = website
    else:
        entry["website"] = None
        if raw.get("website"):
            removed.append("website")

    entry["sources"] = sorted({entry[k]["source"] for k in ("description", "country", "founded", "funding_stage")
                               if entry[k]["source"]})

    # Ohne belegte Beschreibung ist ein Eintrag wertlos und wird verworfen.
    if not name or entry["description"]["value"] is None:
        return None, removed
    return entry, removed
