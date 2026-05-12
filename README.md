# Job Agent: Stephane NANDJOU TONLEU

Surveille automatiquement les offres d'emploi sur 4 plateformes légales,
filtre selon tes critères, génère un Excel et envoie une alerte email.

## Sources
| Plateforme | Type | Légalité |
|---|---|---|
| France Travail | API officielle OAuth2 | ✅ 100% légal |
| APEC | API publique | ✅ 100% légal |
| Welcome to the Jungle | API publique | ✅ 100% légal |
| Cadremploi | RSS feed officiel | ✅ 100% légal |

---

## Installation

### Prérequis
- Python 3.10 ou supérieur
- Pip

```bash
cd C:\Users\Dell\job-agent
pip install -r requirements.txt
```

---

## Configuration

### Étape 1 — Copier le fichier .env
```bash
copy .env.example .env
```

### Étape 2 — France Travail API
1. Va sur **https://francetravail.io**
2. Crée un compte (gratuit)
3. Crée une nouvelle application
4. Abonne-toi au service **"Offres d'emploi v2"**
5. Copie le `client_id` et `client_secret` dans `.env`

### Étape 3 — Gmail App Password
1. Va sur **https://myaccount.google.com/security**
2. Active la **Validation en 2 étapes** si pas déjà fait
3. Cherche **"Mots de passe des applications"**
4. Crée un mot de passe pour **Mail**
5. Copie les 16 caractères générés dans `.env` → `GMAIL_APP_PASSWORD`

### Étape 4 — Remplir .env
```env
FT_CLIENT_ID=ton_client_id
FT_CLIENT_SECRET=ton_client_secret
GMAIL_ADDRESS=audreynandjou1@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
NOTIFY_EMAIL=audreynandjou1@gmail.com
```

---

## Lancement manuel
```bash
python main.py
```

---

## Automatisation — Windows Task Scheduler (toutes les 6h)

1. Ouvre **Planificateur de tâches** (cherche "Task Scheduler" dans le menu Démarrer)
2. Clique **"Créer une tâche de base"**
3. Nom : `Job Agent`
4. Déclencheur : **Quotidien** puis répéter toutes les **6 heures**
5. Action : **Démarrer un programme**
   - Programme : `C:\Users\Dell\AppData\Local\Programs\Python\Python310\python.exe`
   *(adapte le chemin à ta version Python)*
   - Arguments : `C:\Users\Dell\job-agent\main.py`
   - Démarrer dans : `C:\Users\Dell\job-agent`
6. Coche **"Exécuter même si l'utilisateur n'est pas connecté"**

---

## Résultat

Après chaque run :
- **`data/jobs.xlsx`** mis à jour avec les nouvelles offres
- **Email HTML** envoyé à `audreynandjou1@gmail.com` si nouvelles offres

### Colonnes Excel
| Colonne | Description |
|---|---|
| Titre du poste | Intitulé de l'offre |
| Entreprise | Nom de l'entreprise |
| Lien de l'offre | URL cliquable |
| Source | France Travail / APEC / WTTJ / Cadremploi |
| Lieu | Ville / Département |
| Région | Île-de-France ou Autre |
| Salaire | Si mentionné |
| Télétravail | Partiel / Aucun |
| Contrat | CDI |
| Date publication | Date + heure |
| Âge (h) | Heures depuis publication |
| Score /100 | Pertinence calculée automatiquement |
| Résumé description | 500 premiers caractères |
| Compétences détectées | Issues de ton CV |
| Niveau expérience | Junior / Débutant / 2-3 ans / NC |
| Statut | 🆕 Nouveau (à modifier manuellement) |
| Notes personnelles | Champ libre |
| Détecté le | Date/heure de détection |

---
