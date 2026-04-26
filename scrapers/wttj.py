import requests
import hashlib
from datetime import datetime, timedelta, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import SEARCH_KEYWORDS, MAX_JOB_AGE_HOURS

WTTJ_API_URL = "https://api.welcometothejungle.com/api/v1/jobs"
SOURCE = "Welcome to the Jungle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

WTTJ_KEYWORDS = [
    "cybersécurité", "sécurité informatique", "IAM", "SOC analyste",
    "ingénieur réseaux", "cloud azure", "DevOps", "DevSecOps",
    "automatisme", "IT OT", "SCADA", "sûreté fonctionnement",
    "infrastructure IT", "ingénieur systèmes",
]


def _parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _parse_remote(job: dict) -> str:
    remote = job.get("remote", "") or ""
    if isinstance(remote, dict):
        remote = remote.get("label", "") or ""
    remote_lower = str(remote).lower()
    if "partiel" in remote_lower or "hybrid" in remote_lower:
        return "Partiel"
    if "full" in remote_lower or "total" in remote_lower or "complet" in remote_lower:
        return "Télétravail complet"
    return "Aucun"


def _build_job(job: dict, now: datetime) -> Job:
    title = job.get("name", "") or "Sans titre"
    company = (job.get("organization") or {}).get("name", "Entreprise NC")
    office = job.get("office") or {}
    city = office.get("city", "") or ""
    country = office.get("country", {})
    if isinstance(country, dict):
        country = country.get("name", "")
    lieu = f"{city}, {country}".strip(", ") if city else country or "NC"
    region = "Île-de-France" if any(x in lieu.lower() for x in [
        "paris", "île-de-france", "boulogne", "levallois", "neuilly",
        "issy", "montrouge", "clichy", "saint-cloud", "vincennes"
    ]) else "Autre région"
    salary_min = job.get("salary_min") or 0
    salary_max = job.get("salary_max") or 0
    if salary_min and salary_max:
        salary = f"{int(salary_min):,} € - {int(salary_max):,} €".replace(",", " ")
    elif salary_min:
        salary = f"À partir de {int(salary_min):,} €".replace(",", " ")
    else:
        salary = "NC"
    remote = _parse_remote(job)
    description = job.get("description", "") or job.get("profile", "") or ""
    published_at = _parse_date(job.get("published_at") or job.get("created_at", ""))
    age_hours = (now - published_at).total_seconds() / 3600
    slug = job.get("slug", "") or hashlib.md5(f"{title}{company}".encode()).hexdigest()
    org_slug = (job.get("organization") or {}).get("slug", "")
    url = f"https://www.welcometothejungle.com/fr/companies/{org_slug}/jobs/{slug}" \
        if org_slug and slug else "https://www.welcometothejungle.com/fr/jobs"
    job_id = str(job.get("id") or slug)
    exp_level = detect_experience_level(title, description)
    skills = detect_skills(title, description)
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
    print("[Welcome to the Jungle] [pause]  Source désactivée — API rendue privée (partenariat requis)")
    return []
