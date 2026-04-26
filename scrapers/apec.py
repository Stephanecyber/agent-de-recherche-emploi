import requests
import hashlib
from datetime import datetime, timedelta, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import SEARCH_KEYWORDS, MAX_JOB_AGE_HOURS

APEC_SEARCH_URL = "https://www.apec.fr/cms/webservices/rechercheOffre/rechercherOffre"
SOURCE = "APEC"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.apec.fr/candidat/recherche-emploi.html",
}


def _parse_date(date_val) -> datetime:
    if not date_val:
        return datetime.now(timezone.utc)
    try:
        if isinstance(date_val, int):
            return datetime.fromtimestamp(date_val / 1000, tz=timezone.utc)
        return datetime.fromisoformat(str(date_val).replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _parse_remote(offer: dict) -> str:
    teletravail = str(offer.get("télétravail", "") or offer.get("teletravail", "") or "").lower()
    if "partiel" in teletravail or "oui" in teletravail:
        return "Partiel"
    if "total" in teletravail or "complet" in teletravail:
        return "Télétravail complet"
    return "Aucun"


def _build_job(offer: dict, now: datetime) -> Job:
    title = offer.get("intitule", "") or offer.get("titre", "") or "Sans titre"
    company = (offer.get("nomCommercial") or offer.get("entreprise") or {})
    if isinstance(company, dict):
        company = company.get("nom", "Entreprise NC")
    company = company or "Entreprise NC"
    lieu = offer.get("lieuDeTravail", "") or offer.get("lieu", "") or "NC"
    if isinstance(lieu, dict):
        lieu = lieu.get("libelle", "NC")
    salary_min = offer.get("salaireMin", 0) or 0
    salary_max = offer.get("salaireMax", 0) or 0
    if salary_min and salary_max:
        salary = f"Annuel {int(salary_min):,} € - {int(salary_max):,} €".replace(",", " ")
    elif salary_min:
        salary = f"À partir de {int(salary_min):,} €".replace(",", " ")
    else:
        salary = "NC"
    remote = _parse_remote(offer)
    description = offer.get("texteHtml", "") or offer.get("description", "") or ""
    if "<" in description:
        from bs4 import BeautifulSoup
        description = BeautifulSoup(description, "lxml").get_text(separator=" ")
    date_val = offer.get("datePublication") or offer.get("dateCreation")
    published_at = _parse_date(date_val)
    age_hours = (now - published_at).total_seconds() / 3600
    job_id = str(offer.get("numOffre") or offer.get("id") or
                 hashlib.md5(f"{title}{company}{lieu}".encode()).hexdigest())
    url = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi/{job_id}-offre-emploi"
    exp_level = detect_experience_level(title, description)
    skills = detect_skills(title, description)
    region = "Île-de-France" if any(x in lieu.lower() for x in [
        "paris", "île-de-france", "hauts-de-seine", "seine", "yvelines", "essonne", "val-d"
    ]) else "Autre région"
    score = compute_score(title, description, lieu, age_hours, exp_level, region)

    return Job(
        id=job_id,
        title=title,
        company=company,
        url=url,
        source=SOURCE,
        location=lieu,
        region=region,
        salary=salary,
        remote=remote,
        contract_type="CDI",
        published_at=published_at,
        age_hours=round(age_hours, 1),
        description=description[:500] + "..." if len(description) > 500 else description,
        skills_detected=skills,
        experience_level=exp_level,
        relevance_score=score,
    )


def fetch_jobs() -> list:
    print("[APEC] [pause]  Source désactivée — API publique supprimée (les offres APEC sont aussi sur France Travail)")
    return []
