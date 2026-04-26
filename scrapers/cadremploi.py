import feedparser
import hashlib
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import MAX_JOB_AGE_HOURS

SOURCE = "Cadremploi"

CADREMPLOI_KEYWORDS = [
    "cybersécurité", "sécurité informatique", "IAM", "analyste SOC",
    "ingénieur réseaux", "cloud azure", "DevOps", "DevSecOps",
    "automatisme", "sûreté fonctionnement", "infrastructure IT",
    "ingénieur systèmes", "IT OT", "SCADA",
]

RSS_BASE = "https://www.cadremploi.fr/rss"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def _parse_rss_date(entry) -> datetime:
    try:
        if hasattr(entry, "published"):
            return parsedate_to_datetime(entry.published).replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return datetime.now(timezone.utc)


def _parse_remote(summary: str) -> str:
    summary_lower = summary.lower()
    if "télétravail partiel" in summary_lower or "hybride" in summary_lower:
        return "Partiel"
    if "télétravail total" in summary_lower or "full remote" in summary_lower:
        return "Télétravail complet"
    return "Aucun"


def _extract_company(entry) -> str:
    if hasattr(entry, "tags"):
        for tag in entry.tags:
            if hasattr(tag, "label") and tag.label:
                return tag.label
    title = entry.get("title", "")
    if " - " in title:
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[-1].strip()
    return "Entreprise NC"


def _extract_location(entry) -> str:
    summary = entry.get("summary", "")
    for line in summary.split("\n"):
        if any(x in line.lower() for x in ["localisation", "lieu", "ville"]):
            return line.split(":")[-1].strip()
    if hasattr(entry, "tags"):
        for tag in entry.tags:
            term = getattr(tag, "term", "") or ""
            if any(x in term for x in ["Paris", "Île", "Lyon", "Bordeaux", "Marseille", "Nantes"]):
                return term
    return "NC"


def _build_job(entry, now: datetime) -> Job:
    raw_title = entry.get("title", "Sans titre")
    title = raw_title.split(" - ")[0].strip() if " - " in raw_title else raw_title
    company = _extract_company(entry)
    url = entry.get("link", "https://www.cadremploi.fr")
    description = entry.get("summary", "") or ""
    if "<" in description:
        from bs4 import BeautifulSoup
        description = BeautifulSoup(description, "lxml").get_text(separator=" ")
    published_at = _parse_rss_date(entry)
    age_hours = (now - published_at).total_seconds() / 3600
    lieu = _extract_location(entry)
    region = "Île-de-France" if any(x in (lieu + description).lower() for x in [
        "paris", "île-de-france", "hauts-de-seine", "seine", "yvelines", "essonne"
    ]) else "Autre région"
    remote = _parse_remote(description)
    job_id = hashlib.md5(url.encode()).hexdigest()
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
        salary="NC",
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
    print("[Cadremploi] [pause]  Source désactivée — flux RSS supprimé")
    return []
