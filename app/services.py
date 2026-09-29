import re

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from .models import Application, ApplicationDocument, ApplicationStep, Program, User
from .i18n import ROUTE_STEPS


CRITERIA = ("field_match", "language_match", "budget_match", "degree_match", "dormitory_match")

FIELD_ALIASES = {
    "artificial_intelligence": ("artificial intelligence", "ai", "machine learning", "computer science", "applied mathematics", "data science", "software engineering", "applied informatics"),
    "computer_science": ("computer science", "software engineering", "artificial intelligence", "ai", "data science", "applied informatics"),
    "data_science": ("data science", "machine learning", "artificial intelligence", "ai", "computer science", "analytics"),
    "engineering": ("engineering", "computer science", "applied mathematics", "informatics"),
    "economics": ("economics", "business analytics", "finance", "management"),
}


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None


def field_matches(user_field: str | None, program: Program) -> bool | None:
    if not user_field:
        return None
    requested_text = user_field.strip().lower().replace("_", " ")
    requested = requested_text.replace(" ", "_")
    terms = FIELD_ALIASES.get(requested)
    if terms is None and any(_contains_phrase(requested_text, term) for term in ("ai", "artificial intelligence", "machine learning")):
        terms = FIELD_ALIASES["artificial_intelligence"]
    if terms is None:
        terms = tuple(term for aliases in FIELD_ALIASES.values() for term in aliases if _contains_phrase(requested_text, term))
    if not terms:
        terms = (requested_text,)
    haystack = f"{program.field} {program.categories} {program.name}".lower().replace("_", " ")
    return any(_contains_phrase(haystack, term) for term in terms)


def score_program(user: User, program: Program) -> tuple[list[str], list[str]]:
    matched, not_matched = [], []
    checks = {
        "field_match": field_matches(user.field, program),
        "language_match": None if not user.language else user.language.lower() == program.language.lower(),
        "budget_match": None if user.budget is None or program.tuition is None or (user.budget_currency or user.currency or "RUB").upper() != program.currency.upper() else program.tuition <= user.budget,
        "degree_match": bool(user.degree and (user.degree.lower() == program.degree.lower() or (user.degree.lower() == "bachelor" and program.degree.lower() == "specialist"))),
        "dormitory_match": None if not user.needs_dormitory or not program.dormitory_confirmed else program.dormitory,
    }
    for criterion, ok in checks.items():
        if ok is None:
            continue
        (matched if ok else not_matched).append(criterion)
    return matched, not_matched


def recommendations(db: Session, user: User) -> list[tuple[Program, list[str], list[str]]]:
    statement = select(Program).options(joinedload(Program.university)).where(Program.listed.is_(True), Program.admission_cycle == (user.admission_year or 2027))
    if user.degree:
        if user.degree == "bachelor":
            statement = statement.where(Program.degree.in_(("bachelor", "specialist")))
        else:
            statement = statement.where(Program.degree == user.degree)
    if user.language:
        statement = statement.where(Program.language == user.language)
    programs = db.scalars(statement).all()
    scored = [(program, *score_program(user, program)) for program in programs]
    scored.sort(key=lambda x: (-len(x[1]) / max(1, len(x[1]) + len(x[2])), x[0].tuition or float("inf")))
    return scored


def create_application(db: Session, user: User, program: Program, ui_language: str | None = None) -> Application:
    existing = db.scalar(select(Application).where(Application.user_id == user.id, Application.program_id == program.id).options(selectinload(Application.steps), selectinload(Application.documents)))
    if existing:
        return existing
    deadlines = sorted((d for d in program.deadlines if d.admission_cycle == program.admission_cycle), key=lambda d: d.date)
    first_deadline = deadlines[0].date if deadlines else None
    application = Application(user_id=user.id, program_id=program.id)
    db.add(application)
    db.flush()
    locale = ui_language or user.ui_language or "en"
    application_link = program.university.admissions_url or program.source_url
    steps = ROUTE_STEPS.get(locale, ROUTE_STEPS["en"])
    for position, (step_type, title, description) in enumerate(steps, start=1):
        source_url = program.source_url if step_type in ("profile", "language", "exam") else application_link
        db.add(ApplicationStep(application_id=application.id, step_type=step_type, title=title, description=description, source_url=source_url, deadline=first_deadline if step_type == "application" else None, position=position))
    db.flush()
    for document in program.documents:
        db.add(ApplicationDocument(application_id=application.id, document_id=document.id))
    db.commit()
    db.refresh(application)
    return application
