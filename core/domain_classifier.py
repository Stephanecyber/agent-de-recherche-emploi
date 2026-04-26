DOMAIN_RESEAUX = "Reseaux & Securite"
DOMAIN_AUTOMATISME = "Automatisme & Systemes"
DOMAIN_JAVA = "Java & Backend"

_RESEAUX_SIGNALS = [
    "cybersécurité", "cybersecurite", "sécurité informatique", "securite informatique",
    "soc analyste", "analyste soc", "siem", "iam", "rbac", "pam", "pentest",
    "firewall", "vpn", "réseau", "reseau", "réseaux", "reseaux",
    "cloud azure", "azure", "devops", "devsecops", "infrastructure it",
    "infrastructure cloud", "grc", "iso 27001", "threat", "nmap", "wireshark",
    "sécurité applicative", "securite applicative", "sécurité cloud", "securite cloud",
    "administrateur systèmes", "administrateur systemes", "ingénieur systèmes réseaux",
    "ingénieur réseau", "ingenieur reseau", "noc", "support n2", "support n3",
    "ingénieur cloud", "ingenieur cloud", "virtualisation", "vmware", "kubernetes",
]

_AUTOMATISME_SIGNALS = [
    "automatisme", "automaticien", "automate", "automates programmables",
    "scada", "supervision", "contrôle commande", "controle commande",
    "grafcet", "ladder", "fbd", "plc", "codeys", "codesys",
    "ot/it", "it/ot", "ot ", " ot,", "convergence ot",
    "sûreté de fonctionnement", "surete de fonctionnement", "rams", "amdec", "fmea",
    "aéronautique", "aeronautique", "systèmes critiques", "systemes critiques",
    "industrie 4.0", "mes ", "modbus", "profinet", "capteurs", "acquisition",
    "embarqué", "embarque", "microprocesseur", "génie électrique", "genie electrique",
    "ivvq", "vérification validation", "verification validation", "ingénieur systèmes industriels",
]


def classify_job(title: str, description: str) -> str:
    text = (title + " " + description).lower()
    reseaux_score = sum(1 for kw in _RESEAUX_SIGNALS if kw in text)
    auto_score = sum(1 for kw in _AUTOMATISME_SIGNALS if kw in text)

    title_lower = title.lower()
    reseaux_title = sum(2 for kw in _RESEAUX_SIGNALS if kw in title_lower)
    auto_title = sum(2 for kw in _AUTOMATISME_SIGNALS if kw in title_lower)

    total_reseaux = reseaux_score + reseaux_title
    total_auto = auto_score + auto_title

    if total_reseaux >= total_auto:
        return DOMAIN_RESEAUX
    return DOMAIN_AUTOMATISME
