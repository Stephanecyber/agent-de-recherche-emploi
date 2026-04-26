import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import feedparser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

print("=" * 60)
print("TEST NOUVELLES SOURCES")
print("=" * 60)

# --- Indeed France RSS ---
print("\n[Indeed France] Test RSS...")
indeed_urls = [
    "https://fr.indeed.com/rss?q=ingenieur+reseaux&l=France&jt=fulltime",
    "https://fr.indeed.com/rss?q=cybersecurite&l=France",
    "https://fr.indeed.com/jobs?q=ingenieur+reseaux&l=France&format=rss",
]
for url in indeed_urls:
    try:
        feed = feedparser.parse(url)
        status = feed.get("status", "N/A")
        count = len(feed.entries)
        print(f"  {status} — {count} entrées — {url[:60]}")
        if count > 0:
            print(f"  >>> Exemple : {feed.entries[0].get('title', 'N/A')}")
            break
    except Exception as e:
        print(f"  ERR — {e}")

# --- Hellowork ---
print("\n[Hellowork] Test RSS/API...")
hw_urls = [
    "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=ingenieur+reseaux&c=CDI&_format=rss",
    "https://www.hellowork.com/rss?k=ingenieur+reseaux",
    "https://api.hellowork.com/v1/jobs?q=ingenieur+reseaux",
]
for url in hw_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"  {r.status_code} — {url[:60]}")
        if r.status_code == 200:
            print(f"  >>> {r.text[:100]}")
    except Exception as e:
        print(f"  ERR — {e}")

# --- Monster France ---
print("\n[Monster France] Test RSS...")
monster_urls = [
    "https://www.monster.fr/emploi/recherche/?q=ingenieur-reseaux&tm=CDI&format=rss",
    "https://www.monster.fr/rss/jobs?q=ingenieur+reseaux",
]
for url in monster_urls:
    try:
        feed = feedparser.parse(url)
        status = feed.get("status", "N/A")
        count = len(feed.entries)
        print(f"  {status} — {count} entrées — {url[:60]}")
        if count > 0:
            print(f"  >>> Exemple : {feed.entries[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"  ERR — {e}")

# --- Jobijoba ---
print("\n[Jobijoba] Test RSS...")
jb_urls = [
    "https://www.jobijoba.com/fr/rss/?what=ingenieur+reseaux&contract=CDI",
    "https://www.jobijoba.com/rss?q=ingenieur+reseaux",
]
for url in jb_urls:
    try:
        feed = feedparser.parse(url)
        status = feed.get("status", "N/A")
        count = len(feed.entries)
        print(f"  {status} — {count} entrées — {url[:60]}")
        if count > 0:
            print(f"  >>> Exemple : {feed.entries[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"  ERR — {e}")

print("\n" + "=" * 60)
