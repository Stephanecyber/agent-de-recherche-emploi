import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials ---
FT_CLIENT_ID = os.getenv("FT_CLIENT_ID", "")
FT_CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET", "")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "audreynandjou1@gmail.com")
CV_PATH_RESEAUX = os.getenv(
    "CV_PATH_RESEAUX",
    r"C:\Users\Dell\Downloads\CV_NANDJOU_Stephane_Ingenieur_Reseaux_Securite (8).pdf",
)
CV_PATH_AUTOMATISME = os.getenv(
    "CV_PATH_AUTOMATISME",
    r"C:\Users\Dell\Downloads\CV_Stephane_NANDJOU_Automatisme_Industriel_FINAL.pdf",
)
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
CV_PATH_JAVA = os.getenv(
    "CV_PATH_JAVA",
    r"C:\Users\Dell\job-agent\Cv de Brenda\CV_Brenda_KOUDJA.pdf",
)
BRENDA_EMAIL = os.getenv("BRENDA_EMAIL", "Stellagueteu@gmail.com")

# --- Critères de recherche ---
MAX_JOB_AGE_HOURS = 24
MIN_SALARY = 38000
MAX_EXPERIENCE_YEARS = 3

LOCATIONS_IDF = ["75", "77", "78", "91", "92", "93", "94", "95"]
LOCATION_LABEL = "Île-de-France"

# Mots-clés junior/débutant détectés dans les offres (boost score)
JUNIOR_KEYWORDS = [
    "junior", "débutant", "débutant accepté", "première expérience",
    "0-2 ans", "0 à 2 ans", "1 an", "sans expérience", "fresh graduate",
    "jeune diplômé", "young graduate", "entry level", "graduate"
]

# Titres de poste seniors — vérifiés UNIQUEMENT dans le titre de l'offre
# (évite de bloquer les descriptions qui mentionnent ces mots en contexte)
SENIOR_TITLE_KEYWORDS = [
    # Lead / Architecte
    "tech lead", "team lead", "lead engineer", "lead developer", "lead développeur",
    "lead devops", "lead sécurité", "lead infrastructure", "lead réseaux",
    "architecte réseau", "architecte cloud", "architecte sécurité",
    "architecte infrastructure", "architecte solution", "architecte solutions",
    "architecte systèmes", "architecte embarqué", "solutions architect",
    # Responsable / Manager
    "responsable sécurité", "responsable infrastructure", "responsable it",
    "responsable technique", "responsable réseau", "responsable automatisme",
    "responsable systèmes", "responsable devops",
    "manager it", "manager sécurité", "manager infrastructure",
    "chef de projet", "project manager", "it manager",
    # Expert confirmé / référent
    "expert cybersécurité", "expert sécurité", "expert réseaux", "expert cloud",
    "expert automatisme", "expert systèmes", "expert ot", "expert scada",
    "référent technique", "référent sécurité", "référent réseaux",
    "coordinateur technique", "coordinateur it",
    # Direction
    "rssi", "ciso", "dsi", "cto", "directeur technique", "directeur it",
    "directeur sécurité", "directeur infrastructure",
]

# Mots interdits (exclure offres trop seniors) — vérifiés dans titre ET description
SENIOR_EXCLUSION_KEYWORDS = [
    # Années d'expérience explicites
    "4 ans minimum", "5 ans minimum", "6 ans minimum", "7 ans minimum", "8 ans minimum",
    "minimum 4 ans", "minimum 5 ans", "minimum 6 ans", "minimum 7 ans", "minimum 8 ans", "minimum 10 ans",
    "5 ans d'expérience", "6 ans d'expérience", "7 ans d'expérience", "8 ans d'expérience", "10 ans d'expérience",
    "au moins 5 ans", "au moins 6 ans", "au moins 7 ans", "au moins 8 ans", "au moins 10 ans",
    "5 années", "6 années", "7 années", "8 années", "10 années",
    "6 ans", "7 ans", "8 ans", "9 ans", "10 ans",
    "4 à 6 ans", "5 à 8 ans", "5 à 10 ans", "6 à 10 ans",
    # Titres explicitement seniors
    "tech lead", "lead engineer", "lead développeur", "lead developer",
    "senior confirmé", "expert confirmé", "expert senior",
    "directeur", "head of", "manager it", "responsable it",
    "architecte solution", "architecte solutions", "architecte systèmes",
    "cto", "dsi",
]

# --- Mots-clés de recherche par groupe ---
SEARCH_KEYWORDS = [
    # Cybersécurité
    "cybersécurité junior",
    "analyste SOC",
    "ingénieur IAM junior",
    "pentest junior",
    "sécurité cloud junior",
    "DevSecOps junior",
    "consultant cybersécurité junior",
    "GRC sécurité",
    "ISO 27001 junior",
    "SIEM junior",
    "sécurité informatique junior",
    # Réseaux & Infrastructure
    "ingénieur réseaux junior",
    "cloud azure junior",
    "infrastructure IT junior",
    "administrateur systèmes réseaux",
    "ingénieur systèmes réseaux",
    "DevOps junior",
    "ingénieur cloud junior",
    # IT/OT & Industriel
    "cybersécurité OT SCADA",
    "ingénieur IT OT",
    "industrie 4.0 ingénieur",
    "SCADA junior",
    "convergence IT OT",
    # Automatisme & Sûreté
    "ingénieur automaticien junior",
    "sûreté de fonctionnement junior",
    "contrôle commande junior",
    "ingénieur systèmes industriels",
    "RAMS ingénieur",
    # Aéronautique / Défense
    "ingénieur systèmes aéronautiques junior",
    "sûreté fonctionnement aéronautique",
    "ingénieur validation vérification",
]

# --- Titres cibles pour le scoring (match → +40 pts) ---
TARGET_JOB_TITLES = [
    # Cybersécurité
    "consultant cybersécurité", "analyste soc", "analyste cybersécurité",
    "ingénieur sécurité", "ingénieur iam", "administrateur iam", "consultant grc",
    "analyste sécurité applicative", "ingénieur pentest", "consultant iso 27001",
    "auditeur sécurité", "ingénieur sécurité cloud", "devsecops", "threat intelligence",
    "ingénieur siem", "risk manager cybersécurité", "pam", "administrateur pam",
    # Réseaux & Infrastructure
    "ingénieur réseaux", "administrateur réseaux", "ingénieur systèmes réseaux",
    "ingénieur infrastructure", "administrateur systèmes", "ingénieur cloud azure",
    "architecte réseaux", "ingénieur vpn", "ingénieur devops", "ingénieur noc",
    "ingénieur support n2", "ingénieur support n3", "consultant infrastructure cloud",
    # Cloud
    "ingénieur cloud", "cloud security engineer", "ingénieur ci/cd",
    "ingénieur migration cloud", "architecte solutions cloud",
    # IT/OT
    "ingénieur it/ot", "ingénieur réseaux industriels", "cybersécurité ics scada",
    "ingénieur systèmes embarqués", "consultant sécurité ot",
    "ingénieur systèmes critiques", "ingénieur supervision scada",
    # Automatisme
    "ingénieur automaticien", "ingénieur contrôle commande",
    "ingénieur automatisme", "programmeur automates",
    # Sûreté / Aéro
    "ingénieur sûreté de fonctionnement", "ingénieur rams", "analyste amdec",
    "ingénieur validation", "ingénieur vérification", "ingénieur ivvq",
    "ingénieur systèmes aéronautiques",
    # Industrie
    "ingénieur industrie 4.0", "ingénieur mes", "ingénieur scada supervision",
    "ingénieur iot industriel", "ingénieur monitoring",
]

# --- Compétences CV pour détection dans les offres (+30 pts) ---
CV_SKILLS = [
    # Cybersécurité
    "iam", "rbac", "pam", "soc", "siem", "pentest", "owasp", "grc", "iso 27001",
    "sécurité cloud", "azure security", "devsecops", "threat intelligence",
    "nmap", "metasploit", "burp suite", "wireshark", "kali linux",
    # Réseaux & Cloud
    "azure", "vnet", "firewall", "vpn", "tcp/ip", "linux", "windows server",
    "virtualisation", "vmware", "hyper-v", "docker", "kubernetes", "ci/cd",
    # IT/OT
    "scada", "modbus", "profinet", "ot", "it/ot", "supervision",
    # Automatisme
    "grafcet", "ladder", "fbd", "automate", "codeys",
    # Sûreté
    "sûreté de fonctionnement", "rams", "amdec", "fmea",
    # Dev
    "python", "sql", "java", "glpi", "agile", "scrum",
    # Certif / Méthodes
    "teexma", "gns3", "cisco",
]

# ─────────────────────────────────────────────
# Config Brenda KOUDJA — Java & Backend
# ─────────────────────────────────────────────

JAVA_SEARCH_KEYWORDS = [
    "développeur java junior",
    "développeuse java junior",
    "java spring boot junior",
    "java microservices junior",
    "java backend junior",
    "java post-trading",
    "java finance junior",
    "java devops junior",
    "java devsecops",
    "java fullstack junior",
    "java rest api",
    "java hibernate",
    "ingénieur logiciel java",
    "développeur java j2ee",
    "java multithreading",
]

JAVA_ADZUNA_KEYWORDS = [
    "développeur java junior",
    "java spring boot",
    "java microservices",
    "java backend",
    "java devops",
    "java fintech",
    "java post-trading",
    "java rest api",
    "ingénieur java",
]

JAVA_TARGET_TITLES = [
    "développeur java", "développeuse java", "developer java",
    "ingénieur java", "ingénieure java", "ingénieur logiciel java",
    "java backend", "java spring boot", "java microservices",
    "java fullstack", "java post-trading", "java devops",
    "java devsecops", "java fintech", "java rest api",
    "java hibernate", "java j2ee", "java developer",
    "software engineer java", "java multithreading",
]

JAVA_CV_SKILLS = [
    # Java core
    "java", "j2ee", "hibernate", "jfox", "xmlbeans", "slick 2d",
    "spring", "spring boot", "microservices", "multithreading",
    # Finance / protocoles
    "fix", "protocole fix", "post-trading", "listed derivatives",
    # DevOps / CI-CD
    "docker", "jenkins", "gitlab", "sonarqube", "grype",
    "jmeter", "ansible", "haproxy", "prometheus", "grafana",
    "ci/cd", "pipeline", "devops", "devsecops",
    # Backend / API
    "node.js", "nodejs", "rest api", "api rest",
    "maven", "eclipse",
    # Bases de données
    "postgresql", "oracle sql", "sql",
    # Sécurité
    "iam", "owasp", "sécurité applicative",
    # Langages secondaires
    "python", "javascript", "php",
    # Méthodes
    "poo", "uml", "merise", "linux",
]

