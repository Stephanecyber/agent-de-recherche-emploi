# Job Agent — Contexte projet

## Conventions de commits
- Commits **Claude** : préfixe `[claude]` (ex: `[claude] feat(scraper): ...`)
- Commits **Codex** : sans préfixe (ex: `feat(scraper): ...`)
- Avant de modifier un fichier touché par Codex : lire `git log --follow <fichier>`
- **Bug récurrent Codex** : supprime parfois `?.` et `??` — vérifier après ses commits

## Stack
- Python 3.10+
- `requests` — HTTP
- `openpyxl` — Excel
- `beautifulsoup4 + lxml` — parsing HTML descriptions
- `python-dotenv` — chargement `.env`

## Architecture
```
main.py              ← Orchestrateur : collecte → filtre → dédoublonne → Excel → email
config.py            ← Tous les paramètres (keywords, critères, credentials)
scrapers/
  france_travail.py  ← API OAuth2 officielle France Travail
  adzuna.py          ← Adzuna API (agrège les résultats)
core/
  models.py          ← Dataclass Job unifiée (champs phone, email_contact inclus)
  filters.py         ← Filtrage CDI / salaire / expérience / remote
  scoring.py         ← Score pertinence 0–100 + detect_skills + detect_experience_level
  domain_classifier.py ← Classifie chaque offre : RESEAUX / AUTOMATISME / JAVA
  deduplication.py   ← seen_jobs.json (Stéphane) + seen_jobs_brenda.json (Brenda)
  excel_output.py    ← Génère/update data/jobs_*.xlsx (voir détail ci-dessous)
  email_notifier.py  ← Alerte email HTML via Gmail SMTP (voir détail ci-dessous)
data/
  jobs_reseaux_secu.xlsx     ← Généré automatiquement (ne pas committer)
  jobs_automatisme.xlsx      ← Généré automatiquement (ne pas committer)
  jobs_java.xlsx             ← Généré automatiquement (ne pas committer)
  seen_jobs.json             ← Mémoire des offres vues — Stéphane (ne pas committer)
  seen_jobs_brenda.json      ← Mémoire des offres vues — Brenda (ne pas committer)
```

## Lancement
```bash
cd C:\Users\Dell\job-agent
python main.py
```

## Scrapers actifs
| Scraper | Statut | Source |
|---------|--------|--------|
| `france_travail.py` | ✅ Actif | API OAuth2 officielle |
| `adzuna.py` | ✅ Actif | API Adzuna |

## Scrapers supprimés (fichiers supprimés)
- `apec.py` — authentification JavaScript requise (401 sans session)
- `wttj.py` — bloqué réseau
- `cadremploi.py` — RSS bloqué
- `jooble.py` — couverture US uniquement, 0 résultat France
- `arbeitnow.py` — couverture Allemagne uniquement, 0 résultat France

## Critères de filtrage (`core/filters.py`)
- Contrat : CDI uniquement
- Salaire : ≥ 38 000€ brut/an (ignoré si non précisé)
- Expérience : max 3 ans (mots senior/directeur/7 ans+ exclus)
- Localisation : Île-de-France prioritaire + toute la France métropolitaine
- Télétravail : partiel ou aucun (full remote exclu)
- Fraîcheur : offres publiées dans les 24 dernières heures

## Scoring (`core/scoring.py`)
Score 0–100 calculé ainsi :
- **+40 pts** : titre correspond à un `TARGET_JOB_TITLES` de `config.py`
- **+30 pts** : compétences CV détectées dans description (`CV_SKILLS`)
- **+20 pts** : profil junior/débutant détecté
- **+15 pts** : localisation Île-de-France / **+5 pts** reste France
- **+15 pts** : offre < 6h / **+10 pts** < 12h / **+5 pts** < 24h

## Classification domaine (`core/domain_classifier.py`)
Chaque offre reçoit un domaine :
- `DOMAIN_RESEAUX` = "Reseaux & Securite"
- `DOMAIN_AUTOMATISME` = "Automatisme & Systemes"
- `DOMAIN_JAVA` = "Java & Backend" (affecté manuellement dans `main.py`)

Classification Stéphane par comptage de signaux dans titre + description (titre vaut double).
Offres Brenda reçoivent `DOMAIN_JAVA` directement sans classification.

## Excel — Structure des colonnes (`core/excel_output.py`)
Ordre actuel (depuis session 2026-04-26, 20 colonnes) :

| # | Colonne | Largeur | Note |
|---|---------|---------|------|
| 1 | Titre du poste | 38 | gras |
| 2 | Entreprise | 26 | |
| 3 | Lien de l'offre | 42 | hyperlien cliquable |
| 4 | **Statut** | 14 | dropdown + formatage conditionnel |
| 5 | **Date publication** | 20 | format DD/MM/YYYY HH:MM |
| 6 | Score /100 | 12 | coloré vert/jaune/orange selon score |
| 7 | Source | 18 | muted |
| 8 | Lieu | 24 | |
| 9 | Region | 18 | |
| 10 | Salaire | 24 | |
| 11 | Teletravail | 15 | muted |
| 12 | Contrat | 10 | muted |
| 13 | Age (h) | 10 | muted |
| 14 | Resume description | 60 | wrap |
| 15 | Competences detectees | 36 | wrap |
| 16 | Niveau experience | 18 | muted |
| 17 | Telephone | 20 | lien `tel:` cliquable, extrait API FT |
| 18 | Email recruteur | 28 | lien `mailto:` cliquable, extrait API FT |
| 19 | Notes personnelles | 30 | wrap |
| 20 | Detecte le | 20 | format DD/MM/YYYY HH:MM |

### Dropdown Statut (col 4)
Valeurs disponibles via bouton dans chaque cellule :
`Nouveau` / `Postulé` / `Entretien` / `Refusé` / `Abandonné`

### Formatage conditionnel automatique (toute la ligne)
| Statut | Couleur de la ligne |
|--------|---------------------|
| Postulé | Violet/indigo (#E8EAF6, texte #3949AB) |
| Entretien | Cyan clair (#E0F7FA, texte #00695C) |
| Refusé | Rouge pâle (#FFEAEA, texte #C62828) |
| Abandonné | Gris (#F5F5F5, texte #9E9E9E) |
| Nouveau | Couleur alternée normale |

Le formatage se déclenche **automatiquement** dès que l'utilisateur change le statut via le dropdown — aucune action supplémentaire requise.

### Migration colonnes
`_read_existing_jobs()` détecte les colonnes via l'en-tête (lecture dynamique par nom).
Les anciens fichiers Excel (avant le refactoring) sont donc migrés correctement au prochain run.

### Comportement à chaque run
1. Les offres existantes dans le fichier Excel sont relues (avec leurs statuts préservés)
2. Les nouvelles offres sont ajoutées en haut (tri par score décroissant)
3. Les doublons sont éliminés par URL
4. **Auto-purge** : offres "Nouveau" de plus de 24h → supprimées automatiquement
5. Offres non-Nouveau (Postulé, Entretien, Refusé, Abandonné) → conservées en bas du fichier
6. Le fichier entier est réécrit avec le nouveau format
→ Les statuts "Postulé" saisis manuellement ne sont jamais écrasés

## Email (`core/email_notifier.py`)
- Envoi Gmail SMTP SSL (port 465)
- **Stéphane** → `audreynandjou1@gmail.com` — CV Réseaux ou Automatisme selon domaine (`send_alert()`)
- **Brenda** → `Stellagueteu@gmail.com` — Excel `jobs_java.xlsx` + CV Java en PJ (`send_alert_brenda()`)
- Chaque offre déjà "Postulée" dans Excel est marquée **"✓ Déjà postulé"** dans l'email (bouton gris)
- Section "TOP PRIORITE" (score ≥ 80) en haut de l'email
- Colonnes email : Téléphone et Email recruteur inclus dans le tableau HTML
- `_get_applied_urls()` détecte la colonne Statut dynamiquement via l'en-tête (migration safe)

## Profil cible (Stephane NANDJOU TONLEU)
Deux CV :
1. Ingénieur Réseaux & Sécurité — Cybersécurité Junior (ECAM-EPMI 2025)
2. Ingénieur Automaticien — Systèmes Critiques Aéronautiques & Industriels

Compétences clés : IAM/RBAC, Azure, Cybersécurité, Réseaux TCP/IP, SCADA/OT,
Automatisme (Grafcet/Ladder), Python, SQL, Sûreté de fonctionnement, RAMS

## Setup (une seule fois)
1. `cp .env.example .env` puis remplir les credentials
2. `pip install -r requirements.txt`
3. `python main.py`

## Lancement automatique (Windows Task Scheduler)
Voir README.md section "Automatisation".

## Tâche en cours
Aucune tâche en cours.


## Profil Brenda KOUDJA (Java & Backend)
Troisième pipeline — amie ingénieure Java (2 ans BNP Paribas CIB, post-trading/dérivés listés).
- Email : `Stellagueteu@gmail.com`
- CV : `CV_PATH_JAVA` dans `.env` (défaut : `C:\Users\Dell\job-agent\Cv de Brenda\CV_Brenda_KOUDJA.pdf`)
- Fichier Excel généré : `data/jobs_java.xlsx`
- Domaine : `DOMAIN_JAVA = "Java & Backend"` (onglet orange `#E65100`)
- Mots-clés dédiés : `JAVA_SEARCH_KEYWORDS` (France Travail) + `JAVA_ADZUNA_KEYWORDS` (Adzuna)
- Scoring personnalisé : `JAVA_CV_SKILLS` + `JAVA_TARGET_TITLES`
- Email séparé envoyé à Brenda avec Excel + CV en PJ via `send_alert_brenda()`
- Déduplication séparée : `data/seen_jobs_brenda.json`

## Historique des sessions

### Session 2026-04-26
**Implémenté :**
- Ajout du pipeline Java pour Brenda KOUDJA (3ème profil)
- `DOMAIN_JAVA` dans `domain_classifier.py`, `excel_output.py`, `email_notifier.py`, `main.py`
- `config.py` : `JAVA_SEARCH_KEYWORDS`, `JAVA_ADZUNA_KEYWORDS`, `JAVA_CV_SKILLS`, `JAVA_TARGET_TITLES`, `BRENDA_EMAIL`, `CV_PATH_JAVA`
- `models.py` : champs `phone` et `email_contact` ajoutés à la dataclass `Job`
- `scoring.py` : params optionnels `cv_skills` et `target_titles` dans `compute_score()` et `detect_skills()`
- `france_travail.py` : extraction téléphone/email depuis champ `contact`, param `keywords`/`cv_skills`/`target_titles`
- `adzuna.py` : param `keywords`/`cv_skills`/`target_titles` propagés jusqu'à `_build_job()`
- `excel_output.py` : +2 colonnes (Téléphone col 17, Email recruteur col 18), onglet Java orange, auto-purge offres "Nouveau" > 24h, offres non-Nouveau conservées en bas
- `email_notifier.py` : `send_alert_brenda()` envoie à `BRENDA_EMAIL` avec Excel + CV joint
- `deduplication.py` : séparation par profil (`seen_jobs.json` / `seen_jobs_brenda.json`)
- `main.py` : deux collectes séparées (Stéphane / Brenda), déduplication séparée, emails séparés
- Suppression définitive : `jooble.py`, `arbeitnow.py`, `apec.py`, `wttj.py`, `cadremploi.py`
- `config.py` : suppression `JOOBLE_API_KEY`, `ARBEITNOW_KEYWORDS`, `JAVA_ARBEITNOW_KEYWORDS`
- `.env.example` : suppression section Jooble

### Session 2026-04-22
**Implémenté :**
- Suppression des scrapers bloqués (APEC, WTTJ, Cadremploi) de `main.py`
- Suppression de la génération automatique de lettres de motivation de `main.py`
- Refactoring complet de `core/excel_output.py` :
  - Colonnes réordonnées : Statut (col 4) et Date publication (col 5) rapprochés du lien
  - Dropdown openpyxl `DataValidation` sur toute la colonne Statut
  - Formatage conditionnel `FormulaRule` (toute la ligne colorée selon statut)
  - Lecture des colonnes par nom d'en-tête (`_detect_col_map`) — migration safe
- Correction `core/email_notifier.py` : `_get_applied_urls()` détecte col Statut dynamiquement
- Fix bug : `FormulaRule` ne prend pas `dxf=` mais `fill=` et `font=` directement
