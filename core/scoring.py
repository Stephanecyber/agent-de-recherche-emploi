from config import TARGET_JOB_TITLES, CV_SKILLS, JUNIOR_KEYWORDS, LOCATIONS_IDF


def compute_score(title: str, description: str, location: str, age_hours: float,
                  experience_level: str, region: str) -> int:
    score = 0
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = title_lower + " " + desc_lower

    # Correspondance titre cible (+40 pts max)
    title_score = 0
    for target in TARGET_JOB_TITLES:
        if target in title_lower:
            title_score = 40
            break
        words = target.split()
        matches = sum(1 for w in words if w in title_lower)
        partial = int((matches / len(words)) * 30)
        title_score = max(title_score, partial)
    score += title_score

    # Compétences CV détectées dans la description (+30 pts max)
    skills_found = [s for s in CV_SKILLS if s in combined]
    skill_score = min(30, len(skills_found) * 3)
    score += skill_score

    # Profil junior / débutant (+20 pts)
    if experience_level in ("Junior", "Débutant"):
        score += 20
    elif any(k in combined for k in JUNIOR_KEYWORDS):
        score += 15

    # Localisation (+15 pts IDF, +5 pts reste France)
    loc_lower = location.lower() + " " + region.lower()
    idf_labels = ["paris", "île-de-france", "ile-de-france", "hauts-de-seine",
                  "seine-saint-denis", "val-de-marne", "essonne", "yvelines",
                  "val-d'oise", "seine-et-marne"]
    if any(label in loc_lower for label in idf_labels):
        score += 15
    else:
        score += 5

    # Fraîcheur (+15 pts < 6h, +10 pts < 12h, +5 pts < 24h)
    if age_hours < 6:
        score += 15
    elif age_hours < 12:
        score += 10
    elif age_hours < 24:
        score += 5

    return min(score, 100)


def detect_skills(title: str, description: str) -> list:
    combined = (title + " " + description).lower()
    return [s for s in CV_SKILLS if s in combined]


def detect_experience_level(title: str, description: str) -> str:
    combined = (title + " " + description).lower()
    # Débutant / sans expérience
    if any(k in combined for k in [
        "débutant accepté", "débutant", "sans expérience", "0 à 2 ans", "0-2 ans",
        "première expérience", "jeune diplômé", "fresh graduate", "entry level",
        "graduate program", "stage", "alternance",
    ]):
        return "Débutant"
    # Junior — 0 à 2 ans
    if any(k in combined for k in [
        "junior", "1 an d'expérience", "1 an minimum", "1 à 2 ans", "1-2 ans",
        "young graduate", "profil junior", "niveau junior",
    ]):
        return "Junior"
    # 2-3 ans
    if any(k in combined for k in [
        "2 à 3 ans", "2-3 ans", "2 ans minimum", "2 ans d'expérience",
        "expérience souhaitée", "3 ans maximum", "expérience de 2",
    ]):
        return "2-3 ans"
    # 3-5 ans
    if any(k in combined for k in [
        "3 à 5 ans", "3-5 ans", "3 ans minimum", "4 ans", "confirmé", "expérimenté",
        "expérience de 3", "expérience de 4", "3 ans d'expérience", "4 ans d'expérience",
    ]):
        return "3-5 ans"
    # Senior — 5 ans et plus
    if any(k in combined for k in [
        "5 ans", "6 ans", "7 ans", "8 ans", "9 ans", "10 ans",
        "senior", "expert", "tech lead", "lead engineer", "confirmé senior",
        "minimum 5", "minimum 6", "minimum 7", "minimum 8",
        "5 années", "6 années", "7 années", "8 années", "10 années",
    ]):
        return "Senior"
    return "NC"
