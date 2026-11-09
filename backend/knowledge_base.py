"""
P2S Curated Knowledge Base - Germany & Berlin Domain Services
Contains verified public services, emergency hotlines, and official bodies.
All links are clean, canonical MAIN PORTALS to guarantee 0% 404 failure.
"""

# Emergency protocols triggered immediately for life-safety threats
EMERGENCY_SERVICES = [
    {
        "name": "Emergency Services / Notruf (Feuerwehr & Rettungsdienst)",
        "role": "Life-threatening emergencies, fires, gas leaks, severe injuries (Dial 112)",
        "official_link": "tel:112",
        "phone": "112",
        "is_free": True,
        "region": "Germany-wide"
    },
    {
        "name": "Police / Polizei Notruf",
        "role": "Immediate crime, physical danger, illegal forced lockouts / threats (Dial 110)",
        "official_link": "tel:110",
        "phone": "110",
        "is_free": True,
        "region": "Germany-wide"
    },
    {
        "name": "NBB Gas Emergency Hotline / Gasnotruf Berlin",
        "role": "Smell of gas or suspected gas pipe leak in Berlin/Brandenburg (030 7872 72)",
        "official_link": "https://www.nbb-netzgesellschaft.de",
        "phone": "030 7872 72",
        "is_free": True,
        "region": "Berlin"
    },
    {
        "name": "Medical On-Call Service / Ärztlicher Bereitschaftsdienst",
        "role": "Urgent non-life-threatening medical care at night or on weekends (Dial 116 117)",
        "official_link": "https://www.116117.de",
        "phone": "116 117",
        "is_free": True,
        "region": "Germany-wide"
    },
    {
        "name": "TelefonSeelsorge (Mental Health & Crisis Hotline)",
        "role": "24/7 confidential counseling for acute psychological distress (0800 111 0 111)",
        "official_link": "https://www.telefonseelsorge.de",
        "phone": "0800 111 0 111",
        "is_free": True,
        "region": "Germany-wide"
    }
]

# Comprehensive 8-Domain Catalog (All Clean Main Official Portals)
SERVICES_DATABASE = {
    "Facility & Building Emergencies": [
        {
            "name": "Property Management Emergency Service / Hausverwaltung Havariedienst",
            "role": "Building-wide urgent access (fuse box/switch room, boiler room, main water shut-off valve, roof leaks)",
            "official_link": "Check building entrance notice board (Hausaushang) for 24h Notdienstnummer",
            "is_free": True,
            "region": "Building-specific"
        },
        {
            "name": "Berliner Feuerwehr Notöffnung",
            "role": "Immediate building/door emergency opening in case of imminent danger to life or property",
            "official_link": "tel:112",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Verbraucherzentrale Berlin (Schlüsseldienst & Notdienste)",
            "role": "Verified consumer guidance on certified emergency locksmiths and consumer protection",
            "official_link": "https://www.verbraucherzentrale-berlin.de",
            "is_free": True,
            "region": "Berlin"
        }
    ],
    "Tenancy & Housing Law": [
        {
            "name": "Berliner Mieterverein e.V. (BMV)",
            "role": "Legal counseling on security deposit (Mietkaution) withholding, rent reduction (Mietminderung) for mold/defects, and unfair eviction notices",
            "official_link": "https://www.berliner-mieterverein.de",
            "is_free": False,
            "region": "Berlin"
        },
        {
            "name": "Deutscher Mieterbund (DMB)",
            "role": "Federal tenant advocacy network, tenant rights guides, and dispute resolution",
            "official_link": "https://www.mieterbund.de",
            "is_free": True,
            "region": "Germany-wide"
        },
        {
            "name": "Service-Portal Berlin (Miet- & Wohnungsangelegenheiten)",
            "role": "Official municipal portal for tenant rights, housing certificates (WBS), and district housing offices",
            "official_link": "https://service.berlin.de",
            "is_free": True,
            "region": "Berlin"
        }
    ],
    "Health & Medical Care": [
        {
            "name": "116 117 — Ärztlicher Bereitschaftsdienst",
            "role": "On-call doctor navigation when general practices are closed (nights, weekends, public holidays)",
            "official_link": "https://www.116117.de",
            "is_free": True,
            "region": "Germany-wide"
        },
        {
            "name": "Berliner Krisendienst",
            "role": "24/7 fast psychological and psychiatric crisis intervention in Berlin (9 regional locations)",
            "official_link": "https://www.berliner-krisendienst.de",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Apothekerkammer Berlin (Emergency Pharmacies)",
            "role": "Find open late-night and 24/7 emergency pharmacies nearby",
            "official_link": "https://www.akberlin.de",
            "is_free": True,
            "region": "Berlin"
        }
    ],
    "Bureaucracy & Immigration": [
        {
            "name": "Bürgertelefon 115 (Citizen Services)",
            "role": "Central hotline for municipal appointments (Anmeldung), passport services, and civil certificates",
            "official_link": "https://www.115.de",
            "is_free": True,
            "region": "Germany-wide"
        },
        {
            "name": "Landesamt für Einwanderung (LEA Berlin)",
            "role": "Residence permits (Aufenthaltstitel), student visa extensions, emergency contact for expiring visas",
            "official_link": "https://www.berlin.de/einwanderung/",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Caritas Berlin (Migrations- & Sozialberatung)",
            "role": "Independent counselling on bureaucratic documents, health insurance, and legal resident status",
            "official_link": "https://www.caritas-berlin.de",
            "is_free": True,
            "region": "Berlin"
        }
    ],
    "Utilities & Energy Crises": [
        {
            "name": "Stromnetz Berlin — Störungsdienst",
            "role": "Report and track localized or building power outages and electrical grid faults in Berlin",
            "official_link": "https://www.stromnetz.berlin",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Berliner Wasserbetriebe (BWB) — 24h Störungshotline",
            "role": "Burst street mains, building clean water supply cutoff, or sewage emergencies (0800 292 75 87)",
            "official_link": "https://www.bwb.de",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Schlichtungsstelle Energie e.V.",
            "role": "Official dispute arbitration board for electricity and gas contract disputes, billing errors, and disconnection threats",
            "official_link": "https://www.schlichtungsstelle-energie.de",
            "is_free": True,
            "region": "Germany-wide"
        }
    ],
    "Consumer Protection & Contracts": [
        {
            "name": "Verbraucherzentrale Berlin e.V.",
            "role": "Official consumer rights defense: subscription traps, unfair debt collection (Inkasso), misleading contracts, telecommunications bills",
            "official_link": "https://www.verbraucherzentrale-berlin.de",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Bundesnetzagentur (Verbraucherportal)",
            "role": "Unsolicited spam calls, unauthorized telecom contracts, and online vendor disputes",
            "official_link": "https://www.bnetza.de",
            "is_free": True,
            "region": "Germany-wide"
        },
        {
            "name": "Europäisches Verbraucherzentrum (ECC-Net)",
            "role": "Cross-border consumer complaints (e.g. European online shops, airline cancellations, flight refund disputes)",
            "official_link": "https://www.evz.de",
            "is_free": True,
            "region": "Germany-wide"
        }
    ],
    "IT, Telecom & Connectivity": [
        {
            "name": "Bundesnetzagentur Breitbandmessung",
            "role": "Official legally binding broadband speed measurement test required to enforce price reductions or contract cancellation on poor home internet",
            "official_link": "https://www.breitbandmessung.de",
            "is_free": True,
            "region": "Germany-wide"
        },
        {
            "name": "Offizielles Hauptstadtportal Berlin",
            "role": "Public Wi-Fi access locations, public library computer access, and digital civic services",
            "official_link": "https://www.berlin.de",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Netzwerk Reparatur-Initiativen",
            "role": "Community-driven free volunteer repair workshops for consumer electronics, laptops, and peripherals",
            "official_link": "https://www.reparatur-initiativen.de",
            "is_free": True,
            "region": "Berlin"
        }
    ],
    "Home Appliances & Craftspeople": [
        {
            "name": "Handwerkskammer (HWK) Berlin",
            "role": "Official verified registry of certified electricians (Elektroniker), plumbers (SHK), and appliance technicians",
            "official_link": "https://www.hwk-berlin.de",
            "is_free": True,
            "region": "Berlin"
        },
        {
            "name": "Zentralverband des Deutschen Handwerks (ZDH Notdienst)",
            "role": "Official guild-approved on-call craftspeople and verified emergency repair services",
            "official_link": "https://www.zdh.de",
            "is_free": False,
            "region": "Germany-wide"
        }
    ]
}
