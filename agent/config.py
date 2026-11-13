"""Zentrale Einstellungen des Startup Radars.

Alles, was man ohne Programmierkenntnisse anpassen möchte, steht hier:
Modell, Suchbudget und die fünf Recherchefelder.
"""

# Sprachmodell für Recherche und Bewertung (gutes Verhältnis von Qualität zu Kosten)
MODEL = "claude-sonnet-5-5"

# Kostenbremse: maximale Websuchen pro Feld und Lauf
MAX_SEARCHES_PER_FIELD = 4

# Wie viele Startups pro Feld und Lauf höchstens aufgenommen werden
MAX_STARTUPS_PER_FIELD = 5

# Die fünf Felder. Jedes Feld entspricht einer Sparte des Bezugskonzerns
# (siehe agent/DATENMODELL.md). "focus" lenkt die Suche.
FIELDS = {
    "retail": {
        "label": "Retail-Tech / Handel",
        "focus": "Lebensmittel-Filialhandel und Online-Marktplätze: Checkout, Preis- und "
                 "Sortimentsoptimierung, Bestands- und Frischemanagement, Retail Media, "
                 "Kundenerlebnis in der Filiale",
    },
    "food": {
        "label": "Food-Tech / Produktion",
        "focus": "Produktion von Lebensmitteln, Getränken und Verpackungen: alternative "
                 "Proteine, Automatisierung und Qualitätskontrolle in Werken, "
                 "nachhaltige Verpackungen",
    },
    "circular": {
        "label": "Kreislaufwirtschaft / Recycling",
        "focus": "Entsorgung, Sortiertechnik, Kunststoff- und Wertstoffrecycling, Mehrweg- "
                 "und Rücknahmesysteme, Vermeidung von Lebensmittelabfällen",
    },
    "cloud_ai": {
        "label": "Cloud / Cyber Security / Data & AI",
        "focus": "Souveräne europäische Cloud, Cyber Security, Datenplattformen, KI und "
                 "KI-Agenten für Unternehmen",
    },
    "logistics": {
        "label": "Logistik & Supply Chain",
        "focus": "Lagerautomatisierung, Transport und Routenplanung, Bedarfsprognose, "
                 "Transparenz und Resilienz von Lieferketten",
    },
}

# Erlaubte Finanzierungsphasen (feste Werteliste, damit die Filter funktionieren)
FUNDING_STAGES = [
    "Pre-Seed", "Seed", "Series A", "Series B", "Series C+",
    "Bootstrapped", "Öffentlich gefördert", "Übernommen", "Börsennotiert",
]
