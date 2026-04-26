import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from core.domain_classifier import DOMAIN_RESEAUX, DOMAIN_AUTOMATISME, DOMAIN_JAVA

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EXCEL_PATH_RESEAUX = os.path.join(DATA_DIR, "jobs_reseaux_secu.xlsx")
EXCEL_PATH_AUTOMATISME = os.path.join(DATA_DIR, "jobs_automatisme.xlsx")
EXCEL_PATH_JAVA = os.path.join(DATA_DIR, "jobs_java.xlsx")

# Colonnes ordonnées : les plus utiles d'abord (visibles sans scroll)
COLUMNS = [
    ("Titre du poste", 38),        # 1
    ("Entreprise", 26),             # 2
    ("Lien de l'offre", 42),        # 3
    ("Statut", 14),                 # 4
    ("Date publication", 20),       # 5
    ("Niveau experience", 18),      # 6
    ("Score /100", 12),             # 7
    ("Source", 18),                 # 8
    ("Lieu", 24),                   # 9
    ("Region", 18),                 # 10
    ("Salaire", 24),                # 11
    ("Teletravail", 15),            # 12
    ("Contrat", 10),                # 13
    ("Age (h)", 10),                # 14
    ("Resume description", 60),     # 15
    ("Competences detectees", 36),  # 16
    ("Telephone", 18),              # 17
    ("Email recruteur", 30),        # 18
    ("Notes personnelles", 30),     # 19
    ("Detecte le", 20),             # 20
]

# Indices des colonnes clés (1-based)
COL_STATUT = 4
COL_DATE_PUB = 5
COL_NIVEAU = 6
COL_SCORE = 7
COL_LIEN = 3
COL_PHONE = 17
COL_EMAIL_CONTACT = 18
COL_NOTES = 19
COL_DETECTE = 20

HEADER_FILL_RESEAUX = PatternFill("solid", fgColor="1565C0")
HEADER_FILL_AUTOMATISME = PatternFill("solid", fgColor="2E7D32")
HEADER_FILL_JAVA = PatternFill("solid", fgColor="E65100")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10, name="Calibri")

ROW_FILL_ODD = PatternFill("solid", fgColor="FFFFFF")
ROW_FILL_EVEN_RESEAUX = PatternFill("solid", fgColor="EEF4FF")
ROW_FILL_EVEN_AUTOMATISME = PatternFill("solid", fgColor="E8F5E9")
ROW_FILL_EVEN_JAVA = PatternFill("solid", fgColor="FFF3E0")

SCORE_HIGH_FILL = PatternFill("solid", fgColor="C8F5D8")
SCORE_MED_FILL = PatternFill("solid", fgColor="FFF9C4")
SCORE_LOW_FILL = PatternFill("solid", fgColor="FFE0B2")

BORDER_COLOR = "BBCDE5"
THIN = Border(
    left=Side(style="thin", color=BORDER_COLOR),
    right=Side(style="thin", color=BORDER_COLOR),
    top=Side(style="thin", color=BORDER_COLOR),
    bottom=Side(style="thin", color=BORDER_COLOR),
)

TEXT_COLOR = "1A1A2E"
LINK_COLOR_RESEAUX = "1565C0"
LINK_COLOR_AUTOMATISME = "2E7D32"
LINK_COLOR_JAVA = "E65100"
MUTED_COLOR = "546E7A"
NEW_STATUS_COLOR = "1B5E20"

STATUS_VALUES = "Nouveau,Postulé,Entretien,Refusé,Abandonné"
MAX_ROWS = 2000


def _score_fill(score: int) -> PatternFill:
    if score >= 75:
        return SCORE_HIGH_FILL
    if score >= 50:
        return SCORE_MED_FILL
    return SCORE_LOW_FILL


def _score_font_color(score: int) -> str:
    if score >= 75:
        return "1B5E20"
    if score >= 50:
        return "F57F17"
    return "BF360C"


def _add_status_validation_and_cf(ws):
    col_letter = get_column_letter(COL_STATUT)
    data_range = f"{col_letter}2:{col_letter}{MAX_ROWS}"
    row_range = f"A2:{get_column_letter(len(COLUMNS))}{MAX_ROWS}"

    dv = DataValidation(
        type="list",
        formula1=f'"{STATUS_VALUES}"',
        allow_blank=True,
        showDropDown=False,
        showErrorMessage=False,
    )
    ws.add_data_validation(dv)
    dv.sqref = data_range

    ws.conditional_formatting.add(
        row_range,
        FormulaRule(
            formula=[f'${col_letter}2="Postulé"'],
            fill=PatternFill("solid", fgColor="E8EAF6"),
            font=Font(color="3949AB", name="Calibri", size=10),
            stopIfTrue=True,
        ),
    )
    ws.conditional_formatting.add(
        row_range,
        FormulaRule(
            formula=[f'${col_letter}2="Entretien"'],
            fill=PatternFill("solid", fgColor="E0F7FA"),
            font=Font(color="00695C", name="Calibri", size=10),
            stopIfTrue=True,
        ),
    )
    ws.conditional_formatting.add(
        row_range,
        FormulaRule(
            formula=[f'${col_letter}2="Refusé"'],
            fill=PatternFill("solid", fgColor="FFEAEA"),
            font=Font(color="C62828", name="Calibri", size=10),
            stopIfTrue=True,
        ),
    )
    ws.conditional_formatting.add(
        row_range,
        FormulaRule(
            formula=[f'${col_letter}2="Abandonné"'],
            fill=PatternFill("solid", fgColor="F5F5F5"),
            font=Font(color="9E9E9E", name="Calibri", size=10),
        ),
    )


def _create_workbook(domain: str) -> Workbook:
    wb = Workbook()
    ws = wb.active
    if domain == DOMAIN_RESEAUX:
        ws.title = "Reseaux & Securite"
        ws.sheet_properties.tabColor = "1565C0"
        header_fill = HEADER_FILL_RESEAUX
    elif domain == DOMAIN_JAVA:
        ws.title = "Java & Backend"
        ws.sheet_properties.tabColor = "E65100"
        header_fill = HEADER_FILL_JAVA
    else:
        ws.title = "Automatisme & Systemes"
        ws.sheet_properties.tabColor = "2E7D32"
        header_fill = HEADER_FILL_AUTOMATISME

    ws.freeze_panes = "A2"

    for col_idx, (col_name, col_width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN
        ws.column_dimensions[get_column_letter(col_idx)].width = col_width

    ws.row_dimensions[1].height = 32
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}1"

    _add_status_validation_and_cf(ws)

    return wb


def _add_job_row(ws, job, row_idx: int, domain: str):
    is_reseaux = domain == DOMAIN_RESEAUX
    is_java = domain == DOMAIN_JAVA
    if row_idx % 2 != 0:
        base_fill = ROW_FILL_ODD
    elif is_reseaux:
        base_fill = ROW_FILL_EVEN_RESEAUX
    elif is_java:
        base_fill = ROW_FILL_EVEN_JAVA
    else:
        base_fill = ROW_FILL_EVEN_AUTOMATISME

    if is_reseaux:
        link_color = LINK_COLOR_RESEAUX
    elif is_java:
        link_color = LINK_COLOR_JAVA
    else:
        link_color = LINK_COLOR_AUTOMATISME

    score = job.relevance_score

    pub_local = job.published_at.astimezone().replace(tzinfo=None) \
        if job.published_at.tzinfo else job.published_at
    detected_local = job.detected_at.astimezone().replace(tzinfo=None) \
        if job.detected_at.tzinfo else job.detected_at

    values = [
        job.title,                                                      # 1  Titre
        job.company,                                                    # 2  Entreprise
        job.url,                                                        # 3  Lien
        job.status,                                                     # 4  Statut
        pub_local,                                                      # 5  Date publication
        job.experience_level,                                           # 6  Niveau experience
        score,                                                          # 7  Score
        job.source,                                                     # 8  Source
        job.location,                                                   # 9  Lieu
        job.region,                                                     # 10 Region
        job.salary,                                                     # 11 Salaire
        job.remote,                                                     # 12 Teletravail
        job.contract_type,                                              # 13 Contrat
        job.age_hours,                                                  # 14 Age (h)
        job.description,                                                # 15 Resume description
        ", ".join(job.skills_detected) if job.skills_detected else "",  # 16 Competences
        job.phone,                                                      # 17 Telephone
        job.email_contact,                                              # 18 Email recruteur
        job.notes,                                                      # 19 Notes
        detected_local,                                                 # 20 Detecte le
    ]

    for col_idx, value in enumerate(values, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        cell.border = THIN
        cell.alignment = Alignment(
            vertical="center",
            wrap_text=(col_idx in (1, 15, 16, 19)),
            horizontal="left",
        )

        if col_idx == COL_SCORE:
            cell.fill = _score_fill(score)
            cell.font = Font(bold=True, color=_score_font_color(score), name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx == COL_LIEN:
            cell.hyperlink = value or ""
            cell.font = Font(color=link_color, underline="single", name="Calibri", size=10)
            cell.fill = base_fill
        elif col_idx == COL_PHONE and value:
            cell.hyperlink = f"tel:{value}"
            cell.font = Font(color=link_color, underline="single", name="Calibri", size=10)
            cell.fill = base_fill
        elif col_idx == COL_EMAIL_CONTACT and value:
            cell.hyperlink = f"mailto:{value}"
            cell.font = Font(color=link_color, underline="single", name="Calibri", size=10)
            cell.fill = base_fill
        elif col_idx == COL_STATUT:
            val_str = str(value or "")
            is_applied = "postul" in val_str.lower()
            is_new = "Nouveau" in val_str
            if is_applied:
                cell.fill = PatternFill("solid", fgColor="E8EAF6")
                cell.font = Font(color="3949AB", bold=True, name="Calibri", size=10)
            elif is_new:
                cell.fill = PatternFill("solid", fgColor="D4EDDA")
                cell.font = Font(color=NEW_STATUS_COLOR, bold=True, name="Calibri", size=10)
            else:
                cell.fill = base_fill
                cell.font = Font(color=TEXT_COLOR, name="Calibri", size=10)
        elif col_idx in (8, 12, 13, 14):
            cell.fill = base_fill
            cell.font = Font(color=MUTED_COLOR, name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx == COL_NIVEAU:
            cell.fill = base_fill
            cell.font = Font(color=MUTED_COLOR, name="Calibri", size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in (1, 2):
            cell.fill = base_fill
            cell.font = Font(color=TEXT_COLOR, bold=(col_idx == 1), name="Calibri", size=10)
        else:
            cell.fill = base_fill
            cell.font = Font(color=TEXT_COLOR, name="Calibri", size=10)

        if col_idx in (COL_DATE_PUB, COL_DETECTE):
            cell.number_format = "DD/MM/YYYY HH:MM"

    ws.row_dimensions[row_idx].height = 38


def _detect_col_map(ws) -> dict:
    return {
        ws.cell(1, col).value: col
        for col in range(1, ws.max_column + 1)
        if ws.cell(1, col).value
    }


def _read_existing_jobs(ws, domain: str) -> list:
    from core.models import Job

    hdr = _detect_col_map(ws)

    def c(name, fallback=None):
        return hdr.get(name, fallback)

    jobs = []
    for row_idx in range(2, ws.max_row + 1):
        def v(col):
            return ws.cell(row_idx, col).value if col else None

        title = v(c("Titre du poste", 1))
        if not title:
            continue
        try:
            pub = v(c("Date publication", COL_DATE_PUB))
            if isinstance(pub, str):
                pub = datetime.fromisoformat(pub)
            det_raw = v(c("Detecte le", COL_DETECTE))
            detected = datetime.fromisoformat(det_raw) if isinstance(det_raw, str) else det_raw
            skills_raw = v(c("Competences detectees", 16)) or ""
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            job = Job(
                id=str(row_idx),
                title=title or "",
                company=v(c("Entreprise", 2)) or "",
                url=v(c("Lien de l'offre", 3)) or "",
                source=v(c("Source", 8)) or "",
                location=v(c("Lieu", 9)) or "",
                region=v(c("Region", 10)) or "",
                salary=v(c("Salaire", 11)) or "NC",
                remote=v(c("Teletravail", 12)) or "NC",
                contract_type=v(c("Contrat", 13)) or "NC",
                published_at=pub or datetime.now(),
                age_hours=float(v(c("Age (h)", 14)) or 0),
                relevance_score=int(v(c("Score /100", COL_SCORE)) or 0),
                description=v(c("Resume description", 15)) or "",
                skills_detected=skills,
                experience_level=v(c("Niveau experience", COL_NIVEAU)) or "NC",
                status=v(c("Statut", COL_STATUT)) or "Nouveau",
                notes=v(c("Notes personnelles", COL_NOTES)) or "",
                detected_at=detected or datetime.now(),
                domain=domain,
                phone=v(c("Telephone")) or "",
                email_contact=v(c("Email recruteur")) or "",
            )
            jobs.append(job)
        except Exception:
            pass
    return jobs


def _save_domain_jobs(jobs: list, path: str, domain: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    existing = []
    if os.path.exists(path):
        try:
            wb_old = load_workbook(path)
            existing = _read_existing_jobs(wb_old.active, domain)
        except Exception:
            pass

    now_naive = datetime.now()

    def _to_naive(dt):
        if dt is None:
            return datetime.min
        return dt.astimezone().replace(tzinfo=None) if dt.tzinfo else dt

    def _age_h(job) -> float:
        pub = _to_naive(job.published_at)
        if pub == datetime.min:
            return 9999.0
        return (now_naive - pub).total_seconds() / 3600

    new_urls = {j.url for j in jobs}
    fresh_nouveau = []   # Nouveau + age <= 24h  → haut du fichier
    kept_history = []    # statut != Nouveau      → bas du fichier
    purged_count = 0

    for job in existing:
        if job.url in new_urls:
            continue  # remplacé par la version fraîche
        if job.status != "Nouveau":
            kept_history.append(job)
        elif _age_h(job) <= 24:
            fresh_nouveau.append(job)   # encore récent, on garde
        else:
            purged_count += 1           # Nouveau > 24h → purgé

    if purged_count:
        print(f"[Excel] {purged_count} offre(s) 'Nouveau' > 24h purgee(s) de {os.path.basename(path)}")

    # Haut : nouveaux de ce run + frais déjà vus, triés par score desc
    active = sorted(jobs + fresh_nouveau, key=lambda j: (-j.relevance_score, _age_h(j)))

    # Bas : historique non-Nouveau, triés par date desc
    kept_history.sort(key=lambda j: _to_naive(j.published_at), reverse=True)

    jobs_all = active + kept_history

    wb = _create_workbook(domain)
    ws = wb.active
    for idx, job in enumerate(jobs_all, start=2):
        _add_job_row(ws, job, idx, domain)

    try:
        wb.save(path)
    except PermissionError:
        filename = os.path.basename(path)
        print(f"\n[ERREUR] Impossible d'ecrire {filename}")
        print(f"  -> Ferme le fichier dans Excel puis relance.\n")
        raise
    return path


def save_jobs(jobs: list) -> tuple:
    reseaux_jobs = [j for j in jobs if j.domain == DOMAIN_RESEAUX]
    auto_jobs = [j for j in jobs if j.domain == DOMAIN_AUTOMATISME]
    java_jobs = [j for j in jobs if j.domain == DOMAIN_JAVA]

    paths = []
    if reseaux_jobs:
        path = _save_domain_jobs(reseaux_jobs, EXCEL_PATH_RESEAUX, DOMAIN_RESEAUX)
        print(f"Excel Reseaux & Securite : {path} ({len(reseaux_jobs)} offres)")
        paths.append(path)
    if auto_jobs:
        path = _save_domain_jobs(auto_jobs, EXCEL_PATH_AUTOMATISME, DOMAIN_AUTOMATISME)
        print(f"Excel Automatisme & Systemes : {path} ({len(auto_jobs)} offres)")
        paths.append(path)
    if java_jobs:
        path = _save_domain_jobs(java_jobs, EXCEL_PATH_JAVA, DOMAIN_JAVA)
        print(f"Excel Java & Backend : {path} ({len(java_jobs)} offres)")
        paths.append(path)

    return tuple(paths)
