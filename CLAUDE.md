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
  adzuna.py          ← Adzuna API (12 mots-clés, agrège les résultats)
  apec.py            ← BLOQUÉ — ne pas utiliser (erreurs réseau)
  wttj.py            ← BLOQUÉ — ne pas utiliser (erreurs réseau)
  cadremploi.py      ← BLOQUÉ — ne pas utiliser (RSS bloqué)
core/
  models.py          ← Dataclass Job unifiée
  filters.py         ← Filtrage CDI / salaire / expérience / remote
  scoring.py         ← Score pertinence 0–100 + detect_skills + detect_experience_level
  domain_classifier.py ← Classifie chaque offre en RESEAUX ou AUTOMATISME
  deduplication.py   ← seen_jobs.json — évite les doublons entre runs
  excel_output.py    ← Génère/update data/jobs_*.xlsx (voir détail ci-dessous)
  email_notifier.py  ← Alerte email HTML via Gmail SMTP (voir détail ci-dessous)
data/
  jobs_reseaux_secu.xlsx     ← Généré automatiquement (ne pas committer)
  jobs_automatisme.xlsx      ← Généré automatiquement (ne pas committer)
  seen_jobs.json             ← Mémoire des offres vues (ne pas committer)
  lettres/                   ← Lettres de motivation générées (ne plus utiliser)
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
| `adzuna.py` | ✅ Actif | API Adzuna (12 mots-clés) |
| `apec.py` | ❌ Bloqué | Ne plus appeler |
| `wttj.py` | ❌ Bloqué | Ne plus appeler |
| `cadremploi.py` | ❌ Bloqué | Ne plus appeler |

## Scrapers supprimés de main.py
APEC, WTTJ, Cadremploi ont été retirés de l'orchestrateur (`main.py`) car bloqués.
La génération automatique de lettres de motivation (`cover_letter.py`) a aussi été retirée.
Les fichiers sources existent encore dans `scrapers/` et `core/` mais ne sont plus appelés.

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

Classification par comptage de signaux dans titre + description (titre vaut double).

## Excel — Structure des colonnes (`core/excel_output.py`)
Ordre actuel (depuis refactoring 2026-04-22) :

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
| 17 | Notes personnelles | 30 | wrap |
| 18 | Detecte le | 20 | format DD/MM/YYYY HH:MM |

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
2. Les nouvelles offres sont ajoutées en haut (tri par date décroissante)
3. Les doublons sont éliminés par URL
4. Le fichier entier est réécrit avec le nouveau format
→ Les statuts "Postulé" saisis manuellement ne sont jamais écrasés

## Email (`core/email_notifier.py`)
- Envoi Gmail SMTP SSL (port 465)
- Destinataire : `audreynandjou1@gmail.com`
- CV en pièce jointe (PDF) selon le domaine
- Chaque offre déjà "Postulée" dans Excel est marquée **"✓ Déjà postulé"** dans l'email (bouton gris à la place du bouton "Postuler")
- Section "TOP PRIORITE" (score ≥ 80) en haut de l'email
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

## Historique des sessions

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
