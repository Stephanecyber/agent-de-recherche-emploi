import json
import os

SEEN_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "seen_jobs.json")


def _load_seen() -> set:
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def _save_seen(seen: set):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)


def filter_new_jobs(jobs: list) -> list:
    seen = _load_seen()
    new_jobs = [j for j in jobs if j.unique_key() not in seen]
    return new_jobs


def mark_as_seen(jobs: list):
    seen = _load_seen()
    for job in jobs:
        seen.add(job.unique_key())
    _save_seen(seen)
