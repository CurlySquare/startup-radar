"""Zentrale Einstellungen des Startup Radars.

Alles, was man ohne Programmierkenntnisse anpassen möchte, steht hier:
Modell, Suchbudget und die fünf Recherchefelder.
"""

# Sprachmodell für Recherche und Bewertung (gutes Verhältnis von Qualität zu Kosten)
MODEL = "claude-sonnet-5-5"

# Kostenbremse: maximale Websuchen pro Feld und Lauf
MAX_SEARCHES_PER_FIELD = 5

# Wie viele Startups pro Feld und Lauf höchstens aufgenommen werden
MAX_STARTUPS_PER_FIELD = 5

# Die fünf Felder. Jedes Feld entspricht einer Sparte des Bezugskonzerns
# (siehe agent/DATENMODELL.md). "focus" beschreibt das Feld allgemein.
# "subtopics": Jede Woche wird pro Feld ein anderes Unterthema durchsucht
# (Rotation nach Kalenderwoche). So findet der Agent seltener dieselben Firmen.
FIELDS = {
    "retail": {
        "label": "Retail-Tech / Handel",
        "focus": "Lebensmittel-Filialhandel und Online-Marktplätze: Checkout, Preis- und "
                 "Sortimentsoptimierung, Bestands- und Frischemanagement, Retail Media, "
                 "Kundenerlebnis in der Filiale",
        "subtopics": [
            "Self-Checkout und kassenlose Filiale",
            "Preis- und Sortimentsoptimierung mit KI",
            "Bestands- und Frischemanagement, Vermeidung von Lebensmittelabfall im Handel",
            "Retail Media und digitale Werbeflächen in Filialen",
            "Filialbetrieb: Personalplanung, Regal-Monitoring, Filialrobotik",
            "Online-Marktplatz, Quick Commerce und Kundenbindung",
        ],
    },
    "food": {
        "label": "Food-Tech / Produktion",
        "focus": "Produktion von Lebensmitteln, Getränken und Verpackungen: alternative "
                 "Proteine, Automatisierung und Qualitätskontrolle in Werken, "
                 "nachhaltige Verpackungen",
        "subtopics": [
            "Alternative Proteine und Präzisionsfermentation",
            "Automatisierung und Robotik in der Lebensmittelproduktion",
            "Qualitätskontrolle und Lebensmittelsicherheit mit Sensorik und KI",
            "Nachhaltige und recycelbare Verpackungen",
            "Upcycling von Nebenströmen und neue Zutaten",
            "Energie- und Ressourceneffizienz in Produktionswerken",
        ],
    },
    "circular": {
        "label": "Kreislaufwirtschaft / Recycling",
        "focus": "Entsorgung, Sortiertechnik, Kunststoff- und Wertstoffrecycling, Mehrweg- "
                 "und Rücknahmesysteme, Vermeidung von Lebensmittelabfällen",
        "subtopics": [
            "Sortiertechnik und KI-Erkennung von Abfällen",
            "Kunststoffrecycling, mechanisch und chemisch",
            "Mehrweg-, Pfand- und Rücknahmesysteme",
            "Abfall- und Wertstoffdaten, digitale Entsorgungslogistik",
            "Textil-, Elektronik- und Batterierecycling",
            "Lebensmittelrettung und Abfallvermeidung",
        ],
    },
    "cloud_ai": {
        "label": "Cloud / Cyber Security / Data & AI",
        "focus": "Souveräne europäische Cloud, Cyber Security, Datenplattformen, KI und "
                 "KI-Agenten für Unternehmen",
        "subtopics": [
            "Souveräne europäische Cloud und Infrastruktur",
            "Cyber Security: Angriffserkennung, Identitäten, Zero Trust",
            "Sicherheit und Governance für KI und KI-Agenten",
            "Datenplattformen, Datenqualität und Datenaustausch",
            "KI-Agenten für Unternehmensprozesse",
            "Effiziente KI-Infrastruktur: Inferenz, Rechenzentren, Energie",
        ],
    },
    "logistics": {
        "label": "Logistik & Supply Chain",
        "focus": "Lagerautomatisierung, Transport und Routenplanung, Bedarfsprognose, "
                 "Transparenz und Resilienz von Lieferketten",
        "subtopics": [
            "Lagerautomatisierung und Kommissionierrobotik",
            "Transportmanagement, Frachtplattformen und Routenplanung",
            "Bedarfsprognose und Disposition",
            "Transparenz und Risikomanagement in Lieferketten",
            "Letzte Meile und Zustellung, auch autonom",
            "Emissionsarme Logistik: E-Lkw, Laden, Flottenmanagement",
        ],
    },
}

# Erlaubte Finanzierungsphasen (feste Werteliste, damit die Filter funktionieren)
FUNDING_STAGES = [
    "Pre-Seed", "Seed", "Series A", "Series B", "Series C+",
    "Bootstrapped", "Öffentlich gefördert", "Übernommen", "Börsennotiert",
]

# Startup-Definition nach EU-Empfehlung 2026/720 ("innovatives Startup")
STARTUP_MAX_AGE_YEARS = 10      # weniger als 10 Jahre seit Registrierung
STARTUP_MAX_EMPLOYEES = 100     # weniger als 100 Beschäftigte
# (Umsatz/Bilanz max. 10 Mio. € und Innovation: siehe agent/eligibility.py)

# Nachrecherche fehlender Kriterien (Gründungsjahr usw.)
VERIFY_BATCH_SIZE = 4
MAX_SEARCHES_PER_VERIFY = 5
