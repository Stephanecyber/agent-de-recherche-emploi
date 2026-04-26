import re
from config import MIN_SALARY, MAX_EXPERIENCE_YEARS, SENIOR_EXCLUSION_KEYWORDS, SENIOR_TITLE_KEYWORDS
from core.models import Job


def parse_salary(salary_str: str) -> int:
    if not salary_str or salary_str.strip() == "NC":
        return 0
    numbers = re.findall(r'\d[\d\s]*', salary_str.replace(".", "").replace(",", ""))
    values = []
    for n in numbers:
        try:
            v = int(n.replace(" ", ""))
            if v > 500:
                values.append(v)
        except ValueError:
            pass
    if not values:
        return 0
    # Si salaire mensuel (< 10000), convertir en annuel
    result = max(values)
    if result < 10000:
        result = result * 12
    return result


def is_salary_ok(salary_str: str) -> bool:
    if not salary_str or salary_str.strip() == "NC":
        return True  # Garder si non précisé
    parsed = parse_salary(salary_str)
    if parsed == 0:
        return True
    return parsed >= MIN_SALARY


def is_experience_ok(experience_level: str, title: str, description: str) -> bool:
    # Titres seniors bloqués sur le titre uniquement (évite faux positifs dans description)
    title_lower = title.lower()
    for kw in SENIOR_TITLE_KEYWORDS:
        if kw.lower() in title_lower:
            return False
    # Patterns d'années vérifiés sur titre + description (offres Adzuna tronquées)
    text = (title + " " + description).lower()
    for kw in SENIOR_EXCLUSION_KEYWORDS:
        if kw.lower() in text:
            return False
    if experience_level in ("Senior", "3-5 ans"):
        return False
    return True


def is_remote_ok(remote: str) -> bool:
    if remote in ("Partiel", "Aucun", "NC"):
        return True
    if remote == "Télétravail complet":
        return False
    return True


_ALTERNANCE_KEYWORDS = [
    "alternance", "apprentissage", "contrat pro", "contrat de professionnalisation",
    "en alternance", "par alternance", "en apprentissage",
]


def is_contract_ok(contract_type: str) -> bool:
    ct = contract_type.upper().strip()
    if ct in ("ALT", "CDD", "SAI", "MIS", "INT", "FRA", "LIB", "PRO", "APP"):
        return False
    return ct in ("CDI", "NC", "")


def is_not_alternance(title: str, description: str) -> bool:
    text = (title + " " + description).lower()
    return not any(kw in text for kw in _ALTERNANCE_KEYWORDS)


def apply_filters(jobs: list) -> list:
    filtered = []
    for job in jobs:
        if not is_salary_ok(job.salary):
            continue
        if not is_experience_ok(job.experience_level, job.title, job.description):
            continue
        if not is_remote_ok(job.remote):
            continue
        if not is_contract_ok(job.contract_type):
            continue
        if not is_not_alternance(job.title, job.description):
            continue
        filtered.append(job)
    # Trier : plus récent en premier
    filtered.sort(key=lambda j: j.published_at, reverse=True)
    return filtered
