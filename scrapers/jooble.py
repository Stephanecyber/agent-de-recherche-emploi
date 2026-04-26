import requests
import hashlib
from datetime import datetime, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import JOOBLE_API_KEY, SEARCH_KEYWORDS, MAX_JOB_AGE_HOURS

JOOBLE_API_URL = "https://jooble.org/api/{key}"
SOURCE = "Jooble"

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
    "sophia antipolis", "saclay", "marne-la-vallée", "marne la vallee",
]

_IDF_KW = [
    "paris", "île-de-france", "ile-de-france",
    "hauts-de-seine", "seine-saint-denis", "val-de-marne",
    "yvelines", "essonne", "val-d'oise", "seine-et-marne",
    "boulogne", "issy", "levallois", "nanterre", "défense", "defense",
    "neuilly", "courbevoie", "puteaux", "versailles", "saint-denis",
    "montrouge", "clamart", "châtillon", "chatillon",
    "créteil", "creteil", "massy", "évry", "evry",
    "marne-la-vallée", "marne la vallee", "saclay",
]


def _is_france(location: str) -> bool:
    loc = location.lower()
    return any(kw in loc for kw in _FRANCE_KW)


def _parse_region(location: str) -> str:
    loc = location.lower()
    return "Île-de-France" if any(kw in loc for kw in _IDF_KW) else "Autre région"


def _parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _parse_contract(type_str: str) -> str:
    if not type_str:
        return "NC"
    t = type_str.lower()
    if any(k in t for k in ["full-time", "temps plein", "cdi", "permanent", "indéfini", "indefini"]):
        return "CDI"
    return type_str


def _parse_remote(description: str, title: str) -> str:
    combined = (description + " " + title).lower()
    if any(k in combined for k in ["full remote", "100% remote", "télétravail complet"]):
        return "Télétravail complet"
    if any(k in combined for k in ["hybride", "hybrid", "télétravail partiel"]):
        return "Partiel"
    return "Aucun"


def _build_job(item: dict, now: datetime,
               cv_skills: list = None, target_titles: list = None) -> Job:
    title = item.get("title", "Sans titre") or "Sans titre"
    company = item.get("company", "Entreprise NC") or "Entreprise NC"
    location = item.get("location", "NC") or "NC"
    description = item.get("snippet", "") or ""
    salary = item.get("salary", "") or "NC"
    contract = _parse_contract(item.get("type", ""))
    url = item.get("link", "") or ""
    published_at = _parse_date(item.get("updated", "") or item.get("date", ""))
    if not published_at.tzinfo:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_hours = (now - published_at).total_seconds() / 3600
    region = _parse_region(location)
    remote = _parse_remote(description, title)
    job_id = hashlib.md5((url or f"{title}{company}{location}").encode()).hexdigest()
    exp_level = detect_experience_level(title, description)
    skills = detect_skills(title, description, cv_skills=cv_skills)
    score = compute_score(title, description, location, age_hours, exp_level, region,
                          cv_skills=cv_skills, target_titles=target_titles)
    return Job(
        id=f"jooble_{job_id}",
        title=title,
        company=company,
        url=url,
        source=SOURCE,
        location=location,
        region=region,
        salary=salary if salary != "" else "NC",
        remote=remote,
        contract_type=contract,
        published_at=published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc),
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
    api_url = JOOBLE_API_URL.format(key=JOOBLE_API_KEY)
    payload = {"keywords": keyword, "location": "France", "page": 1, "resultsOnPage": 50}
    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.status_code == 200:
            jobs = []
            for item in resp.json().get("jobs", []):
                location = item.get("location", "") or ""
                if not _is_france(location):
                    continue
                job = _build_job(item, now, cv_skills=cv_skills, target_titles=target_titles)
                if job.age_hours <= MAX_JOB_AGE_HOURS:
                    jobs.append(job)
            return jobs
        if resp.status_code == 403:
            print("[Jooble] ERREUR Cle API invalide — verifier JOOBLE_API_KEY dans .env")
        else:
            print(f"[Jooble] HTTP {resp.status_code} pour '{keyword}'")
    except Exception as e:
        print(f"[Jooble] ERR '{keyword}': {e}")
    return []


def fetch_jobs(keywords: list = None, cv_skills: list = None,
               target_titles: list = None) -> list:
    if not JOOBLE_API_KEY:
        print("[Jooble] Source desactivee — JOOBLE_API_KEY non configure dans .env")
        return []

    _keywords = keywords if keywords is not None else SEARCH_KEYWORDS
    now = datetime.now(timezone.utc)
    all_jobs, seen_ids = [], set()

    print(f"[Jooble] Recherche sur {len(_keywords)} mots-cles (France uniquement)...")
    for kw in _keywords:
        for j in _fetch_for_keyword(kw, now, cv_skills=cv_skills, target_titles=target_titles):
            if j.id not in seen_ids:
                seen_ids.add(j.id)
                all_jobs.append(j)

    print(f"[Jooble] OK {len(all_jobs)} offres collectees")
    return all_jobs
