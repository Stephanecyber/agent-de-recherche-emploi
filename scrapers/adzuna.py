import requests
import hashlib
from datetime import datetime, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import SEARCH_KEYWORDS, MAX_JOB_AGE_HOURS, ADZUNA_APP_ID, ADZUNA_APP_KEY

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/fr/search/{page}"
SOURCE = "Adzuna"

ADZUNA_KEYWORDS = [
    "cybersécurité junior",
    "analyste SOC",
    "ingénieur réseaux junior",
    "ingénieur IAM",
    "DevSecOps",
    "cloud azure",
    "infrastructure IT",
    "DevOps junior",
    "SCADA ingénieur",
    "ingénieur systèmes",
    "sûreté fonctionnement",
    "ingénieur automaticien",
]


def _parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _parse_remote(description: str) -> str:
    desc_lower = description.lower()
    if "télétravail partiel" in desc_lower or "hybride" in desc_lower or "hybrid" in desc_lower:
        return "Partiel"
    if "full remote" in desc_lower or "télétravail complet" in desc_lower or "100% remote" in desc_lower:
        return "Télétravail complet"
    return "Aucun"


def _build_job(item: dict, now: datetime,
               cv_skills: list = None, target_titles: list = None) -> Job:
    title = item.get("title", "") or "Sans titre"
    company = (item.get("company") or {}).get("display_name", "Entreprise NC") or "Entreprise NC"
    location_data = item.get("location") or {}
    area = location_data.get("area", [])
    lieu = area[-1] if area else location_data.get("display_name", "NC") or "NC"
    region = "Île-de-France" if any(x in lieu.lower() for x in [
        "paris", "île-de-france", "hauts-de-seine", "seine-saint-denis",
        "val-de-marne", "yvelines", "essonne", "val-d'oise"
    ]) else "Autre région"
    description = item.get("description", "") or ""
    salary_min = item.get("salary_min") or 0
    salary_max = item.get("salary_max") or 0
    if salary_min and salary_max:
        salary = f"{int(salary_min):,} € - {int(salary_max):,} €".replace(",", " ")
    elif salary_min:
        salary = f"À partir de {int(salary_min):,} €".replace(",", " ")
    else:
        salary = "NC"
    remote = _parse_remote(description + " " + title)
    contract_raw = item.get("contract_type", "") or item.get("contract_time", "") or ""
    if "permanent" in contract_raw.lower() or "full_time" in contract_raw.lower():
        contract_type = "CDI"
    elif contract_raw:
        contract_type = contract_raw.upper()
    else:
        contract_type = "NC"
    published_at = _parse_date(item.get("created", ""))
    age_hours = (now - published_at).total_seconds() / 3600
    url = item.get("redirect_url", "") or item.get("adref", "") or "https://www.adzuna.fr"
    job_id = str(item.get("id") or hashlib.md5(f"{title}{company}{lieu}".encode()).hexdigest())
    exp_level = detect_experience_level(title, description)
    skills = detect_skills(title, description, cv_skills=cv_skills)
    score = compute_score(title, description, lieu, age_hours, exp_level, region,
                          cv_skills=cv_skills, target_titles=target_titles)

    return Job(
        id=f"adzuna_{job_id}",
        title=title,
        company=company,
        url=url,
        source=SOURCE,
        location=lieu,
        region=region,
        salary=salary,
        remote=remote,
        contract_type=contract_type,
        published_at=published_at,
        age_hours=round(age_hours, 1),
        description=description[:500] + "..." if len(description) > 500 else description,
        skills_detected=skills,
        experience_level=exp_level,
        relevance_score=score,
        phone="",
        email_contact="",
    )


def _fetch_for_keyword(keyword: str, now: datetime,
                       cv_skills: list = None, target_titles: list = None) -> list:
    jobs = []
    seen_ids = set()
    params_base = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keyword,
        "where": "France",
        "max_days_old": max(1, int(MAX_JOB_AGE_HOURS / 24)),
        "results_per_page": 50,
        "content-type": "application/json",
    }
    try:
        for page in range(1, 4):
            url = ADZUNA_API_URL.format(page=page)
            r = requests.get(url, params={**params_base}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if not results:
                    break
                for item in results:
                    jid = str(item.get("id", ""))
                    if jid and jid in seen_ids:
                        continue
                    if jid:
                        seen_ids.add(jid)
                    job = _build_job(item, now,
                                     cv_skills=cv_skills, target_titles=target_titles)
                    if job.age_hours <= MAX_JOB_AGE_HOURS:
                        jobs.append(job)
                if len(results) < 50:
                    break
            elif r.status_code == 401:
                print("[Adzuna] ERREUR Clé API invalide — vérifier ADZUNA_APP_ID et ADZUNA_APP_KEY dans .env")
                break
            else:
                break
    except Exception as e:
        print(f"[Adzuna] ERR {keyword}: {e}")
    return jobs


def fetch_jobs(keywords: list = None, cv_skills: list = None,
               target_titles: list = None) -> list:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[Adzuna] Source désactivée — ADZUNA_APP_ID / ADZUNA_APP_KEY non configurés dans .env")
        return []

    _keywords = keywords if keywords is not None else ADZUNA_KEYWORDS
    now = datetime.now(timezone.utc)
    all_jobs = []
    seen_global = set()

    print(f"[Adzuna] Recherche sur {len(_keywords)} mots-clés...")
    for kw in _keywords:
        jobs = _fetch_for_keyword(kw, now, cv_skills=cv_skills, target_titles=target_titles)
        for j in jobs:
            if j.id not in seen_global:
                seen_global.add(j.id)
                all_jobs.append(j)

    print(f"[Adzuna] OK {len(all_jobs)} offres collectées")
    return all_jobs
