import sys
import os
from datetime import datetime


sys.path.insert(0, os.path.dirname(__file__))

from scrapers.france_travail import fetch_jobs as fetch_ft
from scrapers.adzuna import fetch_jobs as fetch_adzuna
from core.filters import apply_filters
from core.deduplication import filter_new_jobs, mark_as_seen
from core.excel_output import save_jobs
from core.email_notifier import send_alert
from core.domain_classifier import classify_job, DOMAIN_RESEAUX, DOMAIN_AUTOMATISME


def run():
    run_at = datetime.now()
    print(f"\n{'='*60}")
    print(f"  Job Agent - {run_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}\n")

    print("Collecte des offres...\n")
    all_jobs = []
    all_jobs += fetch_ft()
    all_jobs += fetch_adzuna()

    print(f"\nTotal brut : {len(all_jobs)} offres\n")

    filtered = apply_filters(all_jobs)
    print(f"Apres filtrage : {len(filtered)} offres\n")

    for job in filtered:
        job.domain = classify_job(job.title, job.description)

    reseaux = [j for j in filtered if j.domain == DOMAIN_RESEAUX]
    auto = [j for j in filtered if j.domain == DOMAIN_AUTOMATISME]
    print(f"  Reseaux & Securite    : {len(reseaux)} offres")
    print(f"  Automatisme & Systemes: {len(auto)} offres\n")

    new_jobs = filter_new_jobs(filtered)
    print(f"Nouvelles offres : {len(new_jobs)}\n")

    if not new_jobs:
        print("Aucune nouvelle offre - fin du run.\n")
        return

    new_jobs.sort(key=lambda j: (-j.relevance_score, j.age_hours))

    save_jobs(new_jobs)

    send_alert(new_jobs, run_at)

    mark_as_seen(new_jobs)

    print(f"\n{'='*60}")
    print(f"  Run termine - {len(new_jobs)} offres ajoutees")
    by_source = {}
    for j in new_jobs:
        by_source[j.source] = by_source.get(j.source, 0) + 1
    for src, count in by_source.items():
        print(f"     {src}: {count}")
    top = [j for j in new_jobs if j.relevance_score >= 75]
    print(f"\n  Offres top (score >=75) : {len(top)}")
    for j in top[:5]:
        print(f"     [{j.relevance_score}/100] {j.title} - {j.company} ({j.location}) [{j.domain}]")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
