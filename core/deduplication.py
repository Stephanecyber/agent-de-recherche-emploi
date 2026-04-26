import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Un fichier par profil — évite que les jobs de Stéphane bloquent ceux de Brenda
_SEEN_FILES = {
    "stephane": os.path.join(DATA_DIR, "seen_jobs.json"),
    "brenda":   os.path.join(DATA_DIR, "seen_jobs_brenda.json"),
}


def _seen_path(profile: str) -> str:
    return _SEEN_FILES.get(profile, os.path.join(DATA_DIR, f"seen_jobs_{profile}.json"))


def _load_seen(profile: str = "stephane") -> set:
    path = _seen_path(profile)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))


def _save_seen(seen: set, profile: str = "stephane"):
    path = _seen_path(profile)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)


def filter_new_jobs(jobs: list, profile: str = "stephane") -> list:
    seen = _load_seen(profile)
    return [j for j in jobs if j.unique_key() not in seen]


def mark_as_seen(jobs: list, profile: str = "stephane"):
    seen = _load_seen(profile)
    for job in jobs:
        seen.add(job.unique_key())
    _save_seen(seen, profile)
