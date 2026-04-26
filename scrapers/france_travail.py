import requests
import hashlib
from datetime import datetime, timedelta, timezone
from core.models import Job
from core.scoring import compute_score, detect_skills, detect_experience_level
from config import FT_CLIENT_ID, FT_CLIENT_SECRET, SEARCH_KEYWORDS, MAX_JOB_AGE_HOURS

FT_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
FT_SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
SOURCE = "France Travail"


def _get_token() -> str:
    resp = requests.post(
        FT_TOKEN_URL,
        params={"realm": "/partenaire"},
        data={
            "grant_type": "client_credentials",
            "client_id": FT_CLIENT_ID,
            "client_secret": FT_CLIENT_SECRET,
            "scope": "api_offresdemploiv2 o2dsoffre",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _parse_date(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _parse_remote(offer: dict) -> str:
    teletravail = offer.get("télétravailLibelle", "") or ""
    teletravail_lower = teletravail.lower()
    if "oui" in teletravail_lower or "partiel" in teletravail_lower:
        return "Partiel"
    if "total" in teletravail_lower or "complet" in teletravail_lower:
        return "Télétravail complet"
    return "Aucun"


def _parse_salary(offer: dict) -> str:
    salaire = offer.get("salaire", {}) or {}
    libelle = salaire.get("libelle", "") or ""
    return libelle if libelle else "NC"


def _parse_region(lieu: str) -> str:
    idf_depts = {"75", "77", "78", "91", "92", "93", "94", "95"}
    parts = lieu.split("-")
    if parts:
        dept = parts[0].strip()
        if dept in idf_depts:
            return "Île-de-France"
    return "Autre région"


def _build_job(offer: dict, now: datetime) -> Job:
    title = offer.get("intitule", "Sans titre")
    company = (offer.get("entreprise") or {}).get("nom", "Entreprise NC")
    lieu = (offer.get("lieuTravail") or {}).get("libelle", "NC")
    region = _parse_region(lieu)
    salary = _parse_salary(offer)
    remote = _parse_remote(offer)
    contract = offer.get("typeContrat", "NC")
    description = offer.get("description", "") or ""
    date_str = offer.get("dateCreation", "") or offer.get("dateActualisation", "")
    published_at = _parse_date(date_str)
    age_hours = (now - published_at.replace(tzinfo=timezone.utc)
                 if published_at.tzinfo is None
                 else (now - published_at)).total_seconds() / 3600
    url = (offer.get("origineOffre") or {}).get("urlOrigine", "") or \
          f"https://candidat.francetravail.fr/offres/emploi/detail/{offer.get('id', '')}"
    job_id = offer.get("id") or hashlib.md5(f"{title}{company}{lieu}".encode()).hexdigest()
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
        contract_type=contract,
        published_at=published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc),
        age_hours=round(age_hours, 1),
        description=description[:500] + "..." if len(description) > 500 else description,
        skills_detected=skills,
        experience_level=exp_level,
        relevance_score=score,
    )


def fetch_jobs() -> list:
    if not FT_CLIENT_ID or not FT_CLIENT_SECRET:
        print("[France Travail] ⚠️  Credentials manquants — source ignorée")
        return []

    try:
        token = _get_token()
    except Exception as e:
        print(f"[France Travail] ERREUR Erreur token : {e}")
        return []

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    now = datetime.now(timezone.utc)
    jobs = []
    seen_ids = set()

    for keyword in SEARCH_KEYWORDS:
        params = {
            "motsCles": keyword,
            "typeContrat": "CDI",
            "publieeDepuis": 1,
            "range": "0-49",
        }
        try:
            resp = requests.get(FT_SEARCH_URL, headers=headers, params=params, timeout=15)
            if resp.status_code == 206 or resp.status_code == 200:
                data = resp.json()
                for offer in data.get("resultats", []):
                    job_id = offer.get("id", "")
                    if job_id and job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    try:
                        job = _build_job(offer, now)
                        if job.age_hours <= MAX_JOB_AGE_HOURS:
                            jobs.append(job)
                    except Exception:
                        pass
            elif resp.status_code == 204:
                pass  # Aucun résultat
        except Exception as e:
            print(f"[France Travail] ⚠️  Erreur pour '{keyword}' : {e}")

    print(f"[France Travail] OK {len(jobs)} offres récupérées")
    return jobs
