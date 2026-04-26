import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from scrapers.france_travail import fetch_jobs as fetch_ft
from scrapers.adzuna import fetch_jobs as fetch_adzuna
from scrapers.jooble import fetch_jobs as fetch_jooble
from scrapers.arbeitnow import fetch_jobs as fetch_arbeitnow
from core.filters import apply_filters
from core.deduplication import filter_new_jobs, mark_as_seen
from core.excel_output import save_jobs
from core.email_notifier import send_alert, send_alert_brenda
from core.domain_classifier import classify_job, DOMAIN_RESEAUX, DOMAIN_AUTOMATISME, DOMAIN_JAVA
from config import (
    SEARCH_KEYWORDS, JAVA_SEARCH_KEYWORDS, JAVA_ADZUNA_KEYWORDS,
    JAVA_CV_SKILLS, JAVA_TARGET_TITLES,
    ARBEITNOW_KEYWORDS, JAVA_ARBEITNOW_KEYWORDS,
)


def run():
    run_at = datetime.now()
    print(f"\n{'='*60}")
    print(f"  Job Agent - {run_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}\n")

    # ── Collecte Stéphane (Réseaux & Automatisme) ──────────────
    print(">>> Collecte Stephane (Reseaux / Automatisme)...\n")
    stephane_jobs = []
    stephane_jobs += fetch_ft()
    stephane_jobs += fetch_adzuna()
    stephane_jobs += fetch_jooble()
    stephane_jobs += fetch_arbeitnow()
    print(f"\nTotal brut Stephane : {len(stephane_jobs)} offres\n")

    stephane_filtered = apply_filters(stephane_jobs)
    print(f"Apres filtrage Stephane : {len(stephane_filtered)} offres\n")

    for job in stephane_filtered:
        job.domain = classify_job(job.title, job.description)

    reseaux = [j for j in stephane_filtered if j.domain == DOMAIN_RESEAUX]
    auto = [j for j in stephane_filtered if j.domain == DOMAIN_AUTOMATISME]
    print(f"  Reseaux & Securite    : {len(reseaux)} offres")
    print(f"  Automatisme & Systemes: {len(auto)} offres\n")

    # ── Collecte Brenda (Java & Backend) ───────────────────────
    print(">>> Collecte Brenda (Java & Backend)...\n")
    brenda_jobs = []
    brenda_jobs += fetch_ft(
        keywords=JAVA_SEARCH_KEYWORDS,
        cv_skills=JAVA_CV_SKILLS,
        target_titles=JAVA_TARGET_TITLES,
    )
    brenda_jobs += fetch_adzuna(
        keywords=JAVA_ADZUNA_KEYWORDS,
        cv_skills=JAVA_CV_SKILLS,
        target_titles=JAVA_TARGET_TITLES,
    )
    brenda_jobs += fetch_jooble(
        keywords=JAVA_SEARCH_KEYWORDS,
        cv_skills=JAVA_CV_SKILLS,
        target_titles=JAVA_TARGET_TITLES,
    )
    brenda_jobs += fetch_arbeitnow(
        keywords=JAVA_ARBEITNOW_KEYWORDS,
        cv_skills=JAVA_CV_SKILLS,
        target_titles=JAVA_TARGET_TITLES,
    )
    print(f"\nTotal brut Brenda : {len(brenda_jobs)} offres\n")

    brenda_filtered = apply_filters(brenda_jobs)
    print(f"Apres filtrage Brenda : {len(brenda_filtered)} offres\n")

    for job in brenda_filtered:
        job.domain = DOMAIN_JAVA

    print(f"  Java & Backend : {len(brenda_filtered)} offres\n")

    # ── Déduplication — profils séparés ────────────────────────
    stephane_new = filter_new_jobs(stephane_filtered, profile="stephane")
    brenda_new   = filter_new_jobs(brenda_filtered,   profile="brenda")

    print(f"Nouvelles offres Stephane : {len(stephane_new)}")
    print(f"Nouvelles offres Brenda   : {len(brenda_new)}\n")

    new_jobs = stephane_new + brenda_new

    if not new_jobs:
        print("Aucune nouvelle offre - fin du run.\n")
        return

    new_jobs.sort(key=lambda j: (-j.relevance_score, j.age_hours))

    # ── Sauvegarde Excel ────────────────────────────────────────
    save_jobs(new_jobs)

    # ── Emails ─────────────────────────────────────────────────
    send_alert(stephane_new, run_at)
    send_alert_brenda(brenda_new, run_at)

    mark_as_seen(stephane_new, profile="stephane")
    mark_as_seen(brenda_new,   profile="brenda")

    # ── Résumé ─────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Run termine - {len(new_jobs)} offres ajoutees")
    by_source = {}
    for j in new_jobs:
        by_source[j.source] = by_source.get(j.source, 0) + 1
    for src, count in by_source.items():
        print(f"     {src}: {count}")

    top_s = [j for j in stephane_new if j.relevance_score >= 75]
    print(f"\n  Stephane : {len(stephane_new)} nouvelles offres (top >= 75 : {len(top_s)})")
    for j in top_s[:5]:
        print(f"     [{j.relevance_score}/100] {j.title} - {j.company} [{j.domain}]")

    top_b = [j for j in brenda_new if j.relevance_score >= 75]
    print(f"\n  Brenda   : {len(brenda_new)} nouvelles offres Java (top >= 75 : {len(top_b)})")
    for j in top_b[:5]:
        print(f"     [{j.relevance_score}/100] {j.title} - {j.company} ({j.location})")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
