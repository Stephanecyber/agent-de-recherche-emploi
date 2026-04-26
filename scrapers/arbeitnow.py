import requests
import hashlib
from datetime import datetime, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import ARBEITNOW_KEYWORDS, MAX_JOB_AGE_HOURS

ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"
SOURCE = "Arbeitnow"

_FRANCE_KW = [
    "france", "paris", "île-de-france", "ile-de-france",
    "hauts-de-seine", "seine-saint-denis", "val-de-marne",
    "yvelines", "essonne", "val-d'oise", "seine-et-marne",
    "boulogne", "issy", "levallois", "nanterre", "défense", "defense",
    "neuilly", "courbevoie", "puteaux", "versailles", "saint-denis",
    "montrouge", "clamart", "châtillon", "chatillon",
    "créteil", "creteil", "massy", "évry", "evry",
    "lyon", "marseille", "toulouse", "bordeaux", "lille", "nantes",
    "strasbourg", "rennes", "grenoble", "nice", "montpellier",
    "sophia antipolis", "saclay",
]

_IDF_KW = [
    "paris", "île-de-france", "ile-de-france",
    "hauts-de-seine", "seine-saint-denis", "val-de-marne",
    "yvelines", "essonne", "val-d'oise", "seine-et-marne",
    "boulogne", "issy", "levallois", "nanterre", "défense", "defense",
    "neuilly", "courbevoie", "puteaux", "versailles", "saint-denis",
    "montrouge", "clamart", "créteil", "creteil", "massy", "évry", "evry",
    "saclay",
]


def _is_france(location: str) -> bool:
    loc = location.lower()
    return any(kw in loc for kw in _FRANCE_KW)


def _parse_region(location: str) -> str:
    loc = location.lower()
    return "Île-de-France" if any(kw in loc for kw in _IDF_KW) else "Autre région"


def _parse_remote(is_remote: bool, description: str) -> str:
    if not is_remote:
        return "Aucun"
    desc = description.lower()
    if any(k in desc for k in ["hybride", "hybrid", "partiel"]):
        return "Partiel"
    return "Télétravail complet"


def _parse_contract(job_types: list) -> str:
    if not job_types:
        return "NC"
    for t in job_types:
        if any(k in t.lower() for k in ["full-time", "permanent", "cdi"]):
            return "CDI"
    return ", ".join(job_types)


def _build_job(item: dict, now: datetime,
               cv_skills: list = None, target_titles: list = None) -> Job:
    title = item.get("title", "Sans titre") or "Sans titre"
    company = item.get("company_name", "Entreprise NC") or "Entreprise NC"
    location = item.get("location", "NC") or "NC"
    description = item.get("description", "") or ""
    url = item.get("url", "") or ""
    is_remote = item.get("remote", False)
    job_types = item.get("job_types", []) or []
    created_ts = item.get("created_at", 0)
    published_at = (datetime.fromtimestamp(created_ts, tz=timezone.utc)
                    if created_ts else datetime.now(timezone.utc))
    age_hours = (now - published_at).total_seconds() / 3600
    region = _parse_region(location)
    remote = _parse_remote(is_remote, description)
    contract = _parse_contract(job_types)
    job_id = str(item.get("slug", "")) or hashlib.md5(
        f"{title}{company}{location}".encode()).hexdigest()
    exp_level = detect_experience_level(title, description)
    skills = detect_skills(title, description, cv_skills=cv_skills)
    score = compute_score(title, description, location, age_hours, exp_level, region,
                          cv_skills=cv_skills, target_titles=target_titles)
    return Job(
        id=f"arbeitnow_{job_id}",
        title=title,
        company=company,
        url=url,
        source=SOURCE,
        location=location,
        region=region,
        salary="NC",
        remote=remote,
        contract_type=contract,
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
    try:
        for page in range(1, 4):
            resp = requests.get(
                ARBEITNOW_API_URL,
                params={"search": keyword, "page": page},
                timeout=15,
            )
            if resp.status_code != 200:
                break
            results = resp.json().get("data", [])
            if not results:
                break
            for item in results:
                location = item.get("location", "") or ""
                if not _is_france(location):
                    continue
                job = _build_job(item, now, cv_skills=cv_skills, target_titles=target_titles)
                if job.age_hours <= MAX_JOB_AGE_HOURS:
                    jobs.append(job)
            if len(results) < 10:
                break
    except Exception as e:
        print(f"[Arbeitnow] ERR '{keyword}': {e}")
    return jobs


def fetch_jobs(keywords: list = None, cv_skills: list = None,
               target_titles: list = None) -> list:
    _keywords = keywords if keywords is not None else ARBEITNOW_KEYWORDS
    now = datetime.now(timezone.utc)
    all_jobs, seen_ids = [], set()

    print(f"[Arbeitnow] Recherche sur {len(_keywords)} mots-cles (France uniquement)...")
    for kw in _keywords:
        for j in _fetch_for_keyword(kw, now, cv_skills=cv_skills, target_titles=target_titles):
            if j.id not in seen_ids:
                seen_ids.add(j.id)
                all_jobs.append(j)

    print(f"[Arbeitnow] OK {len(all_jobs)} offres collectees")
    return all_jobs
