import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timezone
from core.models import Job
from core.domain_classifier import DOMAIN_RESEAUX, DOMAIN_AUTOMATISME
from core.cover_letter import generate

# --- Offre exemple Reseaux & Securite ---
job_reseaux = Job(
    id="test_001",
    title="Ingénieur Cybersécurité Junior",
    company="Thales Group",
    url="https://www.thalesgroup.com/offre-exemple",
    source="Test",
    location="Paris (75)",
    region="Île-de-France",
    salary="42 000 € - 48 000 €",
    remote="Partiel",
    contract_type="CDI",
    published_at=datetime.now(timezone.utc),
    age_hours=3.0,
    description=(
        "Nous recherchons un ingénieur cybersécurité junior pour rejoindre notre SOC. "
        "Missions : analyse SIEM, pentest, gestion IAM/RBAC, déploiement Azure, "
        "conformité ISO 27001. Compétences souhaitées : firewall, VPN, Kali Linux, "
        "Nmap, Wireshark. Environnement cloud Azure et DevSecOps."
    ),
    skills_detected=["IAM", "SIEM", "Azure", "Pentest"],
    experience_level="Junior",
    relevance_score=88,
    domain=DOMAIN_RESEAUX,
)

# --- Offre exemple Automatisme ---
job_auto = Job(
    id="test_002",
    title="Ingénieur Automaticien Junior",
    company="Safran Aircraft Engines",
    url="https://www.safran-group.com/offre-exemple",
    source="Test",
    location="Moissy-Cramayel (77)",
    region="Île-de-France",
    salary="40 000 € - 45 000 €",
    remote="Aucun",
    contract_type="CDI",
    published_at=datetime.now(timezone.utc),
    age_hours=5.0,
    description=(
        "Nous recrutons un ingénieur automaticien junior pour nos systèmes industriels aéronautiques. "
        "Missions : programmation automates (GRAFCET, Ladder), supervision SCADA, "
        "sûreté de fonctionnement (RAMS, AMDEC), convergence IT/OT, protocoles PROFINET/Modbus. "
        "Profil systèmes critiques, IVVQ apprécié."
    ),
    skills_detected=["SCADA", "GRAFCET", "RAMS", "AMDEC"],
    experience_level="Junior",
    relevance_score=82,
    domain=DOMAIN_AUTOMATISME,
)

print("Generation des lettres de motivation...\n")

for job in [job_reseaux, job_auto]:
    docx_path, pdf_path = generate(job)
    print(f"[{job.relevance_score}/100] {job.title} - {job.company}")
    print(f"  Word : {docx_path}")
    print(f"  PDF  : {pdf_path if pdf_path else '(non genere)'}")
    print()
