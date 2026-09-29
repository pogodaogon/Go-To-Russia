from contextlib import asynccontextmanager
import asyncio
from datetime import date
import hmac
import hashlib
import json
import math

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from .config import get_settings
from .db import Base, engine, get_db, migrate_schema
from .max_client import MaxClient, callback_id_context
from .i18n import COUNTRY_LABELS, LANGUAGES, programme_content, route_step_text, tr
from .models import Application, ApplicationDocument, ApplicationStep, ProcessedUpdate, Program, ProgramFact, University, User
from .application_documents import render_application_checklist
from .admission_guides import render_admission_guide
from .schemas import ApplicationCreate, ApplicationDocumentResponse, ApplicationDocumentUpdate, ApplicationResponse, ProfileResponse, ProfileUpdate, ProgramResponse, QuestionRequest, RecommendationRequest, UniversityResponse
from .seed import seed_database
from .services import CRITERIA, create_application, recommendations
from .qa import answer_question
from .reminders import reminder_loop


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env == "production":
        if not settings.api_key or len(settings.api_key) < 32 or not settings.max_webhook_secret or len(settings.max_webhook_secret) < 32 or not settings.max_bot_token:
            raise RuntimeError("Production requires API_KEY and MAX_WEBHOOK_SECRET of at least 32 characters, and MAX_BOT_TOKEN")
        if not settings.database_url.startswith("postgresql") or any(placeholder in settings.database_url for placeholder in ("local-dev-only-change-me", "change-this-local-password")):
            raise RuntimeError("Production requires PostgreSQL with a non-default password")
        if not settings.webhook_public_url or not settings.webhook_public_url.startswith("https://"):
            raise RuntimeError("Production requires an HTTPS WEBHOOK_PUBLIC_URL")
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    with next(get_db()) as db:
        seed_database(db)
    reminder_task = asyncio.create_task(reminder_loop(), name="admission-reminders")
    try:
        yield
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Admission Navigator MAX Bot", version="0.1.0", lifespan=lifespan)
settings = get_settings()
max_client = MaxClient()
MAX_UPDATE_MAX_BYTES = 1024 * 1024

ONBOARDING_PROMPTS = {
    "ask_country": {"ru": "Из какой вы страны?", "en": "Which country are you from?", "fr": "De quel pays venez-vous ?", "es": "¿De qué país eres?"},
    "ask_age": {"ru": "Сколько вам лет?", "en": "How old are you?", "fr": "Quel âge avez-vous ?", "es": "¿Cuántos años tienes?"},
    "ask_education": {"ru": "Какое у вас сейчас образование?", "en": "What is your current education?", "fr": "Quel est votre niveau d’études actuel ?", "es": "¿Cuál es tu nivel educativo actual?"},
    "ask_graduation_year": {"ru": "В каком году вы закончили или закончите школу?", "en": "In which year did or will you finish secondary school?", "fr": "En quelle année avez-vous terminé ou terminerez-vous le lycée ?", "es": "¿En qué año terminaste o terminarás la secundaria?"},
    "ask_degree": {"ru": "На какую степень вы поступаете?", "en": "Which degree are you applying for?", "fr": "À quel diplôme souhaitez-vous postuler ?", "es": "¿A qué titulación quieres solicitar plaza?"},
        "ask_field": [("computer_science", {"en": "Computer Science", "ru": "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0442\u0438\u043a\u0430", "fr": "Informatique", "es": "Inform\u00e1tica"}), ("information_security", {"en": "Information Security", "ru": "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u043e\u043d\u043d\u0430\u044f \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c", "fr": "Cybers\u00e9curit\u00e9", "es": "Ciberseguridad"}), ("data_science", {"en": "Data Science", "ru": "\u041d\u0430\u0443\u043a\u0430 \u043e \u0434\u0430\u043d\u043d\u044b\u0445", "fr": "Science des donn\u00e9es", "es": "Ciencia de datos"}), ("engineering", {"en": "Engineering", "ru": "\u0418\u043d\u0436\u0435\u043d\u0435\u0440\u0438\u044f", "fr": "Ing\u00e9nierie", "es": "Ingenier\u00eda"}), ("robotics", {"en": "Robotics", "ru": "\u0420\u043e\u0431\u043e\u0442\u043e\u0442\u0435\u0445\u043d\u0438\u043a\u0430", "fr": "Robotique", "es": "Rob\u00f3tica"}), ("telecommunications", {"en": "Telecommunications", "ru": "\u0422\u0435\u043b\u0435\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438", "fr": "T\u00e9l\u00e9communications", "es": "Telecomunicaciones"}), ("applied_mathematics", {"en": "Applied Mathematics", "ru": "\u041f\u0440\u0438\u043a\u043b\u0430\u0434\u043d\u0430\u044f \u043c\u0430\u0442\u0435\u043c\u0430\u0442\u0438\u043a\u0430", "fr": "Math\u00e9matiques appliqu\u00e9es", "es": "Matem\u00e1ticas aplicadas"}), ("communications", {"en": "Communications and media", "ru": "\u041a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438 \u0438 \u043c\u0435\u0434\u0438\u0430", "fr": "Communication et m\u00e9dias", "es": "Comunicaci\u00f3n y medios"}), ("medicine", {"en": "Medicine and health", "ru": "\u041c\u0435\u0434\u0438\u0446\u0438\u043d\u0430 \u0438 \u0437\u0434\u043e\u0440\u043e\u0432\u044c\u0435", "fr": "M\u00e9decine et sant\u00e9", "es": "Medicina y salud"}), ("economics", {"en": "Economics and business", "ru": "\u042d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0430 \u0438 \u0431\u0438\u0437\u043d\u0435\u0441", "fr": "\u00c9conomie et commerce", "es": "Econom\u00eda y negocios"})],
    "ask_field": {"ru": "????? ??????????? ??? ???????????", "en": "Which field are you interested in?", "fr": "Quel domaine vous int?resse ?", "es": "?Qu? campo te interesa?"},
    "ask_language": {"ru": "На каком языке вы хотите учиться?", "en": "Which language do you want to study in?", "fr": "Dans quelle langue souhaitez-vous étudier ?", "es": "¿En qué idioma quieres estudiar?"},
    "ask_russian_level": {"ru": "Какой у вас уровень русского языка?", "en": "What is your Russian level?", "fr": "Quel est votre niveau de russe ?", "es": "¿Cuál es tu nivel de ruso?"},
    "ask_admission_year": {"ru": "В каком году планируете поступать?", "en": "Which year do you plan to start?", "fr": "En quelle année souhaitez-vous commencer ?", "es": "¿En qué año planeas empezar?"},
    "ask_quota": {"ru": "Хотите рассмотреть государственную квоту?", "en": "Would you like to explore a government quota?", "fr": "Souhaitez-vous étudier la possibilité d’un quota d’État ?", "es": "¿Quieres explorar la posibilidad de una cuota estatal?"},
    "ask_budget_currency": {"ru": "В какой валюте указать годовой бюджет?", "en": "Which currency should we use for your yearly budget?", "fr": "Quelle devise utiliser pour votre budget annuel ?", "es": "¿Qué moneda usamos para tu presupuesto anual?"},
    "ask_budget": {"ru": "Каков максимальный бюджет за обучение в год? Введите число.", "en": "What is your maximum yearly tuition budget? Enter a number.", "fr": "Quel est votre budget annuel maximal pour les frais de scolarité ? Entrez un nombre.", "es": "¿Cuál es tu presupuesto máximo anual de matrícula? Escribe un número."},
    "ask_dormitory": {"ru": "Нужно ли вам общежитие?", "en": "Do you need a dormitory?", "fr": "Avez-vous besoin d’un logement universitaire ?", "es": "¿Necesitas residencia universitaria?"},
}


def _onboarding_prompt(locale: str, state: str) -> str:
    return ONBOARDING_PROMPTS.get(state, ONBOARDING_PROMPTS["ask_country"]).get(locale, ONBOARDING_PROMPTS.get(state, ONBOARDING_PROMPTS["ask_country"])["en"])


def _onboarding_buttons(locale: str, state: str) -> list[list[dict]]:
    options = {
        "ask_education": [("secondary", {"en": "Secondary school", "ru": "Среднее образование", "fr": "Études secondaires", "es": "Educación secundaria"}), ("undergraduate", {"en": "Some university", "ru": "Неоконченное высшее", "fr": "Études universitaires en cours", "es": "Estudios universitarios"})],
        "ask_degree": [("bachelor", {"en": "Bachelor", "ru": "Бакалавриат", "fr": "Licence", "es": "Grado"}), ("master", {"en": "Master", "ru": "Магистратура", "fr": "Master", "es": "Máster"})],
        "ask_field": [("computer_science", {"en": "Computer Science", "ru": "Информатика", "fr": "Informatique", "es": "Informática"}), ("information_security", {"en": "Information Security", "ru": "Информационная безопасность", "fr": "Cybersécurité", "es": "Ciberseguridad"}), ("data_science", {"en": "Data Science", "ru": "Наука о данных", "fr": "Science des données", "es": "Ciencia de datos"}), ("engineering", {"en": "Engineering", "ru": "Инженерия", "fr": "Ingénierie", "es": "Ingeniería"}), ("robotics", {"en": "Robotics", "ru": "Робототехника", "fr": "Robotique", "es": "Robótica"}), ("telecommunications", {"en": "Telecommunications", "ru": "\u0422\u0435\u043b\u0435\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438", "fr": "T\u00e9l\u00e9communications", "es": "Telecomunicaciones"}), ("applied_mathematics", {"en": "Applied Mathematics", "ru": "\u041f\u0440\u0438\u043a\u043b\u0430\u0434\u043d\u0430\u044f \u043c\u0430\u0442\u0435\u043c\u0430\u0442\u0438\u043a\u0430", "fr": "Math\u00e9matiques appliqu\u00e9es", "es": "Matem\u00e1ticas aplicadas"}), ("communications", {"en": "Communications and media", "ru": "\u041a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438 \u0438 \u043c\u0435\u0434\u0438\u0430", "fr": "Communication et m\u00e9dias", "es": "Comunicaci\u00f3n y medios"}), ("medicine", {"en": "Medicine and health", "ru": "Медицина и здоровье", "fr": "Médecine et santé", "es": "Medicina y salud"}), ("economics", {"en": "Economics and business", "ru": "Экономика и бизнес", "fr": "Économie et commerce", "es": "Economía y negocios"})],
        "ask_language": [("english", {"en": "English", "ru": "Английский", "fr": "Anglais", "es": "Inglés"}), ("russian", {"en": "Russian", "ru": "Русский", "fr": "Russe", "es": "Ruso"})],
        "ask_russian_level": [("none", {"en": "None", "ru": "Не знаю", "fr": "Aucun", "es": "Ninguno"}), ("basic", {"en": "Basic", "ru": "Начальный", "fr": "Débutant", "es": "Básico"}), ("intermediate", {"en": "Intermediate", "ru": "Средний", "fr": "Intermédiaire", "es": "Intermedio"}), ("advanced", {"en": "Advanced", "ru": "Продвинутый", "fr": "Avancé", "es": "Avanzado"})],
        "ask_quota": [("yes", {"en": "Yes", "ru": "Да", "fr": "Oui", "es": "Sí"}), ("no", {"en": "No", "ru": "Нет", "fr": "Non", "es": "No"})],
        "ask_budget_currency": [("RUB", {"en": "RUB", "ru": "RUB", "fr": "RUB", "es": "RUB"}), ("USD", {"en": "USD", "ru": "USD", "fr": "USD", "es": "USD"})],
        "ask_dormitory": [("yes", {"en": "Yes", "ru": "Да", "fr": "Oui", "es": "Sí"}), ("no", {"en": "Not necessary", "ru": "Не обязательно", "fr": "Pas nécessaire", "es": "No es necesario"})],
    }
    if state not in options:
        return []
    buttons = [_button(labels.get(locale, labels["en"]), f"onboard:{state}:{value}") for value, labels in options[state]]
    if state == "ask_field":
        return [buttons[index:index + 3] for index in range(0, len(buttons), 3)]
    return [buttons]


@app.middleware("http")
async def protect_api(request: Request, call_next):
    if settings.app_env == "production" and request.url.path not in ("/health", "/webhook/max"):
        supplied_key = request.headers.get("x-api-key", "")
        if not settings.api_key or not hmac.compare_digest(supplied_key, settings.api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "admission-navigator", "max_configured": bool(settings.max_bot_token)}


@app.get("/universities", response_model=list[UniversityResponse])
def list_universities(q: str | None = None, limit: int = 50, db: Session = Depends(get_db)) -> list[University]:
    if not 1 <= limit <= 100:
        raise HTTPException(400, "limit must be between 1 and 100")
    statement = select(University).order_by(University.name).limit(limit)
    if q:
        statement = statement.where(University.name.ilike(f"%{q[:100]}%"))
    return list(db.scalars(statement).all())


@app.get("/programs", response_model=list[ProgramResponse])
def list_programs(degree: str | None = None, language: str | None = None, field: str | None = None, admission_cycle: int = 2027, limit: int = 100, db: Session = Depends(get_db)) -> list[dict]:
    if not 1 <= limit <= 200:
        raise HTTPException(400, "limit must be between 1 and 200")
    statement = select(Program).where(Program.listed.is_(True), Program.admission_cycle == admission_cycle).options(
        joinedload(Program.university), selectinload(Program.requirements), selectinload(Program.documents),
        selectinload(Program.deadlines), selectinload(Program.facts),
    ).order_by(Program.name).limit(limit)
    if degree:
        statement = statement.where(Program.degree == degree)
    if language:
        statement = statement.where(Program.language == language)
    if field:
        statement = statement.where(Program.field.ilike(f"%{field[:100]}%"))
    programs = db.scalars(statement).all()
    return [_program_view(program) for program in programs]


def _program_view(program: Program) -> dict:
    return {
        "id": program.id, "university": program.university.name, "university_short_name": program.university.short_name,
        "name": program.name, "degree": program.degree, "field": program.field, "language": program.language,
        "duration_years": program.duration_years, "tuition": program.tuition, "currency": program.currency,
        "dormitory": program.dormitory if program.dormitory_confirmed else None, "description": program.description,
        "requirements": [{"type": r.type, "value": r.value, "source_url": r.source_url, "verified_at": r.verified_at} for r in program.requirements],
        "documents": [{"name": d.name, "required": d.required, "description": d.description, "source_url": d.source_url, "verified_at": d.verified_at} for d in program.documents],
        "deadlines": [{"type": d.type, "date": d.date, "admission_cycle": d.admission_cycle, "source_url": d.source_url, "verified_at": d.verified_at} for d in program.deadlines if d.admission_cycle == program.admission_cycle],
        "source_url": program.source_url, "verified_at": program.verified_at, "admission_cycle": program.admission_cycle,
        "facts": [{"key": f.key, "value": f.value, "source_url": f.source_url, "verified_at": f.verified_at, "admission_cycle": f.admission_cycle} for f in program.facts],
    }


def _owned_application(db: Session, application_id: int, user_id: int) -> Application:
    application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user_id).options(
        selectinload(Application.steps), selectinload(Application.documents).joinedload(ApplicationDocument.document),
        joinedload(Application.program).joinedload(Program.university),
    ))
    if not application:
        raise HTTPException(404, "Application not found")
    return application


@app.post("/users/{max_user_id}/profile", response_model=ProfileResponse)
def upsert_profile(max_user_id: int, payload: ProfileUpdate, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.max_user_id == max_user_id))
    if not user:
        user = User(max_user_id=max_user_id)
        db.add(user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    required = ("country", "age", "current_education", "graduation_year", "degree", "field", "language", "russian_level", "budget", "admission_year")
    missing = [field for field in required if getattr(user, field) is None]
    if missing:
        raise HTTPException(422, {"message": "Profile is incomplete", "missing_fields": missing})
    user.state = "profile_complete"
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{max_user_id}/profile", response_model=ProfileResponse)
def get_profile(max_user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.max_user_id == max_user_id))
    if not user:
        raise HTTPException(404, "Profile not found")
    return user


@app.post("/recommendations")
def get_recommendations(payload: RecommendationRequest, db: Session = Depends(get_db)) -> list[dict]:
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    original_field = user.field
    if payload.query:
        user.field = payload.query
    result = []
    for program, matched, not_matched in recommendations(db, user):
        result.append({
            "program_id": program.id,
            "university": program.university.name,
            "university_short_name": program.university.short_name,
            "program": program.name,
            "language": program.language,
            "tuition": program.tuition,
            "currency": program.currency,
            "dormitory": program.dormitory if program.dormitory_confirmed else None,
            "match_count": len(matched),
            "criteria_count": len(matched) + len(not_matched),
            "unknown_count": len(CRITERIA) - len(matched) - len(not_matched),
            "matched": matched,
            "not_matched": not_matched,
            "source_url": program.source_url,
            "budget_comparable": user.budget is not None and (user.budget_currency or user.currency or "RUB").upper() == program.currency.upper() and program.tuition is not None,
        })
    user.field = original_field
    return result


@app.post("/questions")
async def ask_question(payload: QuestionRequest, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    try:
        return await answer_question(db, payload.question, user.ui_language)
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        return {"answer": "I could not confirm this from official university sources. Please check the admissions office.", "sources": [], "grounded": False}


@app.get("/comparison")
def compare_programs(program_ids: str, db: Session = Depends(get_db)) -> list[dict]:
    """Return a normalized comparison for two or three programme ids."""
    try:
        ids = [int(value) for value in program_ids.split(",") if value.strip()]
    except ValueError as exc:
        raise HTTPException(400, "program_ids must be comma-separated integers") from exc
    if not 2 <= len(ids) <= 3 or len(ids) != len(set(ids)):
        raise HTTPException(400, "Choose two or three programmes")
    programs = db.scalars(select(Program).where(Program.id.in_(ids), Program.listed.is_(True)).options(joinedload(Program.university), selectinload(Program.requirements), selectinload(Program.documents), selectinload(Program.deadlines))).all()
    if len(programs) != len(set(ids)):
        raise HTTPException(404, "One or more programmes not found")
    return [{
        "program_id": program.id,
        "university": program.university.short_name,
        "program": program.name,
        "degree": program.degree,
        "field": program.field,
        "language": program.language,
        "tuition": program.tuition,
        "currency": program.currency,
        "dormitory": program.dormitory if program.dormitory_confirmed else None,
        "duration_years": program.duration_years,
        "requirements": [{"type": item.type, "value": item.value, "source_url": item.source_url, "verified_at": item.verified_at} for item in program.requirements],
        "documents": [{"name": item.name, "required": item.required, "source_url": item.source_url} for item in program.documents],
        "deadlines": [{"type": item.type, "date": item.date, "source_url": item.source_url, "verified_at": item.verified_at} for item in program.deadlines],
        "admission_routes": program.admission_routes,
        "source_url": program.source_url,
    } for program in programs]


@app.get("/programs/{program_id}", response_model=ProgramResponse)
def get_program(program_id: int, db: Session = Depends(get_db)) -> dict:
    program = db.scalar(select(Program).where(Program.id == program_id, Program.listed.is_(True)).options(joinedload(Program.university), selectinload(Program.requirements), selectinload(Program.documents), selectinload(Program.deadlines), selectinload(Program.facts)))
    if not program:
        raise HTTPException(404, "Program not found")
    return _program_view(program)


@app.post("/applications", response_model=ApplicationResponse)
def add_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, payload.user_id)
    program = db.scalar(select(Program).where(Program.id == payload.program_id, Program.listed.is_(True)))
    if not user or not program:
        raise HTTPException(404, "User or program not found")
    return application_view(create_application(db, user, program, user.ui_language))


def application_view(application: Application) -> dict:
    completed = sum(step.status == "completed" for step in application.steps)
    next_step = next((step.title for step in application.steps if step.status != "completed"), None)
    return {"id": application.id, "program_id": application.program_id, "program_name": application.program.name, "university": application.program.university.short_name, "status": application.status, "completed_steps": completed, "total_steps": len(application.steps), "next_step": next_step, "steps": application.steps, "documents": [{"id": item.id, "document_id": item.document_id, "name": item.document.name, "required": item.document.required, "description": item.document.description, "source_url": item.document.source_url, "status": item.status, "comment": item.comment} for item in application.documents]}


@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)) -> dict:
    application = db.scalar(select(Application).where(Application.id == application_id).options(selectinload(Application.steps), selectinload(Application.documents).joinedload(ApplicationDocument.document), joinedload(Application.program).joinedload(Program.university)))
    if not application:
        raise HTTPException(404, "Application not found")
    return application_view(application)


@app.get("/users/{max_user_id}/applications", response_model=list[ApplicationResponse])
def list_applications(max_user_id: int, db: Session = Depends(get_db)) -> list[dict]:
    user = db.scalar(select(User).where(User.max_user_id == max_user_id))
    if not user:
        return []
    applications = db.scalars(select(Application).where(Application.user_id == user.id).options(selectinload(Application.steps), selectinload(Application.documents).joinedload(ApplicationDocument.document), joinedload(Application.program).joinedload(Program.university))).all()
    return [application_view(item) for item in applications]


@app.post("/application-steps/{step_id}/complete")
def complete_step(step_id: int, db: Session = Depends(get_db)) -> dict:
    step = db.get(ApplicationStep, step_id)
    if not step:
        raise HTTPException(404, "Step not found")
    step.status = "completed"
    application = step.application
    if all(item.status == "completed" for item in application.steps):
        application.status = "completed"
    db.commit()
    return {"id": step.id, "status": step.status, "application_status": application.status}


@app.put("/applications/{application_id}/documents/{application_document_id}")
def update_application_document(application_id: int, application_document_id: int, user_id: int, payload: ApplicationDocumentUpdate, db: Session = Depends(get_db)) -> dict:
    application = _owned_application(db, application_id, user_id)
    item = next((doc for doc in application.documents if doc.id == application_document_id), None)
    if not item:
        raise HTTPException(404, "Application document not found")
    item.status = payload.status
    item.comment = payload.comment
    db.commit()
    return {"id": item.id, "status": item.status, "comment": item.comment}


def _user_from_update(update: dict) -> tuple[int | None, str | None, str | None]:
    message = update.get("message") or {}
    callback = update.get("callback") or {}
    # For message_callback, message.sender is often the bot itself. Prefer
    # callback.user/update.user, which identifies the person who pressed it.
    sender = callback.get("user") or update.get("user") or message.get("sender") or {}
    user_id = sender.get("user_id") or sender.get("id")
    body = message.get("body") or {}
    text = message.get("text") or body.get("text")
    payload = callback.get("payload") or callback.get("data")
    return user_id, text, payload


def _button(text: str, payload: str) -> dict:
    return {"type": "callback", "text": text, "payload": payload}


async def _handle_max_update(update: dict, db: Session) -> None:
    update_type = update.get("update_type")
    user_id, text, payload = _user_from_update(update)
    if not user_id:
        return
    # This bot operates in direct dialogs: POST /messages?user_id=... expects
    # the user's ID, not the separate chat_id carried by bot_started updates.
    try:
        send_id = int(user_id)
    except (TypeError, ValueError):
        return
    user = db.scalar(select(User).where(User.max_user_id == int(user_id)))
    if not user:
        user = User(max_user_id=int(user_id), first_name=((update.get("user") or {}).get("first_name")))
        db.add(user)
        db.commit()
        db.refresh(user)

    if update_type == "bot_started" or (text and text.strip().lower() in ("/start", "start")):
        user.state = "choose_ui_language"
        db.commit()
        await max_client.send_message(send_id, tr(user.ui_language, "choose_language"), [[_button(name, f"ui_lang:{code}") for code, name in LANGUAGES.items()]])
        return

    action = payload or text or ""
    normalized_action = action.strip().lower()
    locale = user.ui_language if user.ui_language in LANGUAGES else "en"
    if action == "menu":
        menu_buttons = [
            [_button(tr(locale, "menu_programs"), "nav:programs")],
            [_button({"ru": "Найти по направлению", "en": "Search by subject", "fr": "Rechercher un domaine", "es": "Buscar por área"}.get(locale, "Search by subject"), "nav:search")],
            [_button(tr(locale, "menu_applications"), "nav:applications")],
            [_button(tr(locale, "menu_language"), "nav:language"), _button(tr(locale, "menu_help"), "nav:help")],
        ]
        await max_client.send_message(send_id, tr(locale, "menu"), menu_buttons)
    elif action.startswith("nav:"):
        normalized_action = "/" + action.split(":", 1)[1]
        if normalized_action == "/language":
            await max_client.send_message(send_id, tr(locale, "choose_language"), [[_button(name, f"ui_lang:{code}") for code, name in LANGUAGES.items()]])
        elif normalized_action == "/help":
            await max_client.send_message(send_id, tr(locale, "help"))
        elif normalized_action == "/search":
            user.state = "ask_search"
            db.commit()
            await max_client.send_message(send_id, {"ru": "Напишите направление, например: искусственный интеллект или инженерия.", "en": "Tell me the field, for example: artificial intelligence or engineering.", "fr": "Indiquez le domaine, par exemple : intelligence artificielle ou ingénierie.", "es": "Escribe el área, por ejemplo: inteligencia artificial o ingeniería."}.get(locale, "Tell me the field you want to study."))
        elif normalized_action == "/programs":
            if user.state == "profile_complete":
                await show_recommendations(user, db, send_id)
            else:
                user.state = "ask_country"
                db.commit()
                country_labels = COUNTRY_LABELS[locale]
                await max_client.send_message(send_id, _onboarding_prompt(locale, "ask_country"), [[_button(country_labels[0], "country:Nigeria"), _button(country_labels[1], "country:other")]])
        elif normalized_action == "/applications":
            applications = db.scalars(select(Application).where(Application.user_id == user.id).options(selectinload(Application.steps), joinedload(Application.program).joinedload(Program.university))).all()
            if not applications:
                await max_client.send_message(send_id, tr(locale, "no_applications"))
            else:
                buttons = [[_button(f"{item.program.university.short_name} — {item.program.name[:28]}", f"route:{item.id}")] for item in applications]
                await max_client.send_message(send_id, tr(locale, "applications"), buttons)
        elif normalized_action == "/search":
            user.state = "ask_search"
            db.commit()
            await max_client.send_message(send_id, "Tell me the field you want to study.")
    elif normalized_action == "/language":
        await max_client.send_message(send_id, tr(locale, "choose_language"), [[_button(name, f"ui_lang:{code}") for code, name in LANGUAGES.items()]])
    elif normalized_action == "/search":
        user.state = "ask_search"
        db.commit()
        await max_client.send_message(send_id, {"ru": "Напишите направление, например: искусственный интеллект или инженерия.", "en": "Tell me the field, for example: artificial intelligence or engineering.", "fr": "Indiquez le domaine, par exemple : intelligence artificielle ou ingénierie.", "es": "Escribe el área, por ejemplo: inteligencia artificial o ingeniería."}.get(locale, "Tell me the field you want to study."))
    elif action.startswith("ui_lang:"):
        choice = action.split(":", 1)[1]
        if choice not in LANGUAGES:
            return
        user.ui_language = choice
        is_startup_choice = user.state == "choose_ui_language"
        if is_startup_choice:
            user.state = "ask_country"
        db.commit()
        if is_startup_choice:
            country_question = tr(choice, "ask_country")
            country_labels = COUNTRY_LABELS[choice]
            await max_client.send_message(send_id, f"{tr(choice, 'welcome', bot=settings.bot_name)}\n\n{country_question}", [[_button(country_labels[0], "country:Nigeria"), _button(country_labels[1], "country:other")]])
        else:
            await max_client.send_message(send_id, tr(choice, "language_changed"))
    elif normalized_action == "/help":
        await max_client.send_message(send_id, tr(locale, "help"))
    elif normalized_action == "/reset":
        user.country = user.degree = user.field = user.language = None
        user.age = user.current_education = user.graduation_year = user.russian_level = None
        user.budget = None
        user.budget_currency = "RUB"
        user.needs_dormitory = False
        user.interested_in_quota = False
        user.admission_year = None
        user.state = "ask_country"
        db.commit()
        country_labels = COUNTRY_LABELS[locale]
        await max_client.send_message(send_id, tr(locale, "reset", country=tr(locale, "ask_country")), [[_button(country_labels[0], "country:Nigeria"), _button(country_labels[1], "country:other")]])
    elif normalized_action == "/programs":
        if user.state == "profile_complete":
            await show_recommendations(user, db, send_id)
        else:
            user.state = "ask_country"
            db.commit()
            country_labels = COUNTRY_LABELS[locale]
            await max_client.send_message(send_id, tr(locale, "profile_first", country=tr(locale, "ask_country")), [[_button(country_labels[0], "country:Nigeria"), _button(country_labels[1], "country:other")]])
    elif normalized_action == "/applications":
        applications = db.scalars(select(Application).where(Application.user_id == user.id).options(selectinload(Application.steps), joinedload(Application.program).joinedload(Program.university))).all()
        if not applications:
            await max_client.send_message(send_id, tr(locale, "no_applications"))
        else:
            buttons = [[_button(f"{item.program.university.short_name} — {item.program.name[:28]}", f"route:{item.id}")] for item in applications]
            await max_client.send_message(send_id, tr(locale, "applications"), buttons)
    elif user.state == "ask_search":
        if not action.strip():
            await max_client.send_message(send_id, "Please enter a field of study.")
            return
        user.field = action.strip()[:120]
        user.state = "profile_complete"
        db.commit()
        await show_recommendations(user, db, send_id)
    elif action.startswith("country:") or user.state == "ask_country":
        if action.startswith("country:") and action.endswith(":other"):
            user.state = "ask_country"
            db.commit()
            await max_client.send_message(send_id, _onboarding_prompt(locale, "ask_country"))
            return
        user.country = action.split(":", 1)[1].strip()[:80] if action.startswith("country:") else action.strip()[:80]
        if not user.country or user.country.lower() == "other":
            await max_client.send_message(send_id, _onboarding_prompt(locale, "ask_country"))
            return
        user.state = "ask_age"
        db.commit()
        await max_client.send_message(send_id, _onboarding_prompt(locale, user.state))
    elif user.state in {"ask_age", "ask_education", "ask_graduation_year", "ask_degree", "ask_field", "ask_language", "ask_russian_level", "ask_admission_year", "ask_quota", "ask_budget_currency", "ask_budget", "ask_dormitory"}:
        current_state = user.state
        state_aliases = {"degree": "ask_degree", "field": "ask_field", "language": "ask_language", "dorm": "ask_dormitory"}
        if action.startswith("onboard:"):
            _, submitted_state, value = action.split(":", 2)
            if state_aliases.get(submitted_state, submitted_state) != current_state:
                await max_client.send_message(send_id, _onboarding_prompt(locale, current_state), _onboarding_buttons(locale, current_state))
                return
        else:
            value = action
            for prefix in ("degree:", "field:", "language:", "dorm:"):
                if action.startswith(prefix):
                    value = action[len(prefix):]
                    break
        try:
            if current_state == "ask_age":
                parsed = int(value)
                if not 16 <= parsed <= 100: raise ValueError
                user.age = parsed
            elif current_state == "ask_education":
                if value not in ("secondary", "undergraduate"): raise ValueError
                user.current_education = value
            elif current_state == "ask_graduation_year":
                parsed = int(value)
                if not 2000 <= parsed <= 2100: raise ValueError
                user.graduation_year = parsed
            elif current_state == "ask_degree":
                if value not in ("bachelor", "master"): raise ValueError
                user.degree = value
            elif current_state == "ask_field": user.field = value[:120]
            elif current_state == "ask_language":
                if value not in ("english", "russian"): raise ValueError
                user.language = value
            elif current_state == "ask_russian_level":
                if value not in ("none", "basic", "intermediate", "advanced"): raise ValueError
                user.russian_level = value
            elif current_state == "ask_admission_year":
                parsed = int(value)
                if not settings.admission_year <= parsed <= settings.admission_year + 5: raise ValueError
                user.admission_year = parsed
            elif current_state == "ask_quota":
                if value.lower() not in ("yes", "no", "true", "false", "да", "нет"): raise ValueError
                user.interested_in_quota = value.lower() in ("yes", "true", "да")
            elif current_state == "ask_budget_currency":
                if value.upper() not in ("RUB", "USD"): raise ValueError
                user.budget_currency = value.upper()
            elif current_state == "ask_budget":
                amount = value.replace(" ", "")
                if "," in amount and amount.rsplit(",", 1)[1].isdigit() and len(amount.rsplit(",", 1)[1]) == 3:
                    amount = amount.replace(",", "")
                else:
                    amount = amount.replace(",", ".")
                parsed = float(amount)
                if not math.isfinite(parsed) or parsed < 0: raise ValueError
                user.budget = parsed
            elif current_state == "ask_dormitory":
                if value.lower() not in ("yes", "no", "true", "false", "да", "нет"): raise ValueError
                user.needs_dormitory = value.lower() in ("yes", "true", "да")
        except (ValueError, TypeError):
            await max_client.send_message(send_id, _onboarding_prompt(locale, current_state))
            return
        flow = ["ask_age", "ask_education", "ask_graduation_year", "ask_degree", "ask_field", "ask_language", "ask_russian_level", "ask_admission_year", "ask_quota", "ask_budget_currency", "ask_budget", "ask_dormitory"]
        next_state = flow[flow.index(current_state) + 1] if current_state in flow and current_state != flow[-1] else None
        if next_state:
            user.state = next_state
            db.commit()
            await max_client.send_message(send_id, _onboarding_prompt(locale, next_state), _onboarding_buttons(locale, next_state))
        else:
            user.state = "profile_complete"
            db.commit()
            await show_recommendations(user, db, send_id)
    elif action == "recommendations":
        await show_recommendations(user, db, send_id)
    elif action.startswith("recommendations:language:"):
        language = action.rsplit(":", 1)[1]
        if language not in {"english", "russian"}:
            return
        user.language = language
        db.commit()
        await show_recommendations(user, db, send_id)
    elif action.startswith("program:"):
        try:
            program_id = int(action.split(":", 1)[1])
        except ValueError:
            await max_client.send_message(send_id, "Invalid programme selection.")
            return
        program = db.scalar(select(Program).where(Program.id == program_id, Program.listed.is_(True)).options(joinedload(Program.university), selectinload(Program.requirements), selectinload(Program.documents), selectinload(Program.deadlines), selectinload(Program.facts)))
        if program:
            deadline = min((d.date for d in program.deadlines if d.admission_cycle == program.admission_cycle), default=None)
            tuition = f"{program.tuition:,.0f} {program.currency}/{ {'ru': 'год', 'en': 'year', 'fr': 'an', 'es': 'año'}.get(locale, 'year') }" if program.tuition is not None else tr(locale, "price_unknown")
            housing = tr(locale, "housing_yes" if program.dormitory else "housing_no") if program.dormitory_confirmed else tr(locale, "housing_unknown")
            description, requirement_values, document_values = programme_content(program, locale)
            requirement_text = "\n".join(f"• {value}\n  {r.source_url}" for r, value in zip(program.requirements, requirement_values))
            document_text = "\n".join(f"• {name}: {value}\n  {d.source_url}" for d, (name, value) in zip(program.documents, document_values))
            old_fees = [fact for fact in program.facts if fact.key == "tuition" and fact.admission_cycle != program.admission_cycle]
            prior_fee_text = "\n".join(f"{fact.admission_cycle}: {fact.value}; verified {fact.verified_at} — {fact.source_url}" for fact in old_fees)
            labels = (tr(locale, "language_label"), tr(locale, "tuition_label"), tr(locale, "housing_label"), tr(locale, "deadline_label"), tr(locale, "deadline_unknown"), tr(locale, "requirements"), tr(locale, "documents"), tr(locale, "program_page"))
            fee_note = f"\nPrevious-cycle fee reference (not a {program.admission_cycle} quote):\n{prior_fee_text}" if prior_fee_text else ""
            deadline_note = deadline.isoformat() if deadline else labels[4]
            await max_client.send_message(send_id, f"{program.university.short_name}: {program.name}\n\n{labels[0]}: {program.language}\n{labels[1]}: {tuition}{fee_note}\n{labels[2]}: {housing}\n{labels[3]}: {deadline_note}\nAdmission route: {program.admission_routes}\nVerified: {program.verified_at}\n\n{description}\n\n{labels[5]}:\n{requirement_text}\n\n{labels[6]}:\n{document_text}\n\n{labels[7]}: {program.source_url}", [[_button(tr(locale, "apply"), f"apply:{program.id}"), _button(tr(locale, "more_programs"), "recommendations")]])
    elif action.startswith("compare:"):
        try:
            ids = [int(value) for value in action.split(":", 1)[1].split(",")]
        except ValueError:
            ids = []
        if not 2 <= len(ids) <= 3 or len(ids) != len(set(ids)):
            await max_client.send_message(send_id, "Invalid comparison selection.")
            return
        programs = db.scalars(select(Program).where(Program.id.in_(ids), Program.listed.is_(True)).options(joinedload(Program.university))).all()
        if len(programs) >= 2:
            lines = [tr(locale, "comparison")]
            for program in programs:
                tuition = f"{program.tuition:,.0f} {program.currency}" if program.tuition is not None else tr(locale, "price_unknown")
                housing = tr(locale, "housing_yes" if program.dormitory else "housing_no") if program.dormitory_confirmed else tr(locale, "not_confirmed")
                language = {"english": tr(locale, "english"), "russian": "Русский" if locale == "ru" else "Russian"}.get(program.language, program.language)
                admission = program.admission_routes or ("Не подтверждено" if locale == "ru" else "Not confirmed")
                lines.append(f"\n{program.university.short_name} — {program.name}\n{tr(locale, 'language_short')}: {language}\n{tr(locale, 'tuition_label')}: {tuition}\n{tr(locale, 'housing_label')}: {housing}\n{tr(locale, 'duration')}: {program.duration_years} {tr(locale, 'years')}\n{('Поступление' if locale == 'ru' else 'Admission')}: {admission}\n{('Источник' if locale == 'ru' else 'Source')}: {program.source_url}")
            await max_client.send_message(send_id, "\n".join(lines), [[_button(tr(locale, "show_programs"), "recommendations")]])
    elif action.startswith("apply:"):
        try:
            program_id = int(action.split(":", 1)[1])
        except ValueError:
            await max_client.send_message(send_id, "Invalid programme selection.")
            return
        program = db.scalar(select(Program).where(Program.id == program_id, Program.listed.is_(True)))
        if program:
            application = create_application(db, user, program, locale)
            first_title, _ = route_step_text(application.steps[0].step_type, locale)
            await max_client.send_message(send_id, tr(locale, "route_created", program=program.name, count=len(application.steps), step=first_title), [[_button(tr(locale, "open_route"), f"route:{application.id}"), _button(tr(locale, "to_programs"), "recommendations")]])
    elif action.startswith("route:"):
        try:
            application_id = int(action.split(":", 1)[1])
        except ValueError:
            await max_client.send_message(send_id, "Invalid route selection.")
            return
        application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id).options(selectinload(Application.steps), selectinload(Application.documents).joinedload(ApplicationDocument.document), joinedload(Application.program).joinedload(Program.university)))
        if application:
            lines = [f"{application.program.university.short_name} — {application.program.name}", tr(locale, "route_disclaimer")]
            for step in application.steps:
                mark = "✅" if step.status == "completed" else "⬜"
                title, description = route_step_text(step.step_type, locale)
                lines.append(f"{mark} {step.position}. {title}\n{description}\n{'Источник' if locale == 'ru' else 'Source'}: {step.source_url}")
            lines.extend(("", render_admission_guide(application.program.university.short_name, locale)))
            document_buttons = []
            if application.documents:
                lines.append("\n" + ("Документы:" if locale == "ru" else "Documents:"))
                for item in application.documents:
                    status = {"missing": "⬜", "ready": "✅", "needs_review": "🟡"}.get(item.status, "⬜")
                    lines.append(f"{status} {item.document.name} — {item.status}\n{item.document.source_url}")
                    if item.status != "ready":
                        label = "Готово" if locale == "ru" else "Mark ready"
                        document_buttons.append([_button(f"{label}: {item.document.name[:22]}", f"doc_ready:{application.id}:{item.id}")])
            next_step = next((s for s in application.steps if s.status != "completed"), None)
            buttons = [[_button(tr(locale, "mark_step"), f"confirm_step:{application.id}:{next_step.id}")]] if next_step else []
            buttons.extend(document_buttons)
            buttons.append([_button(tr(locale, "export_checklist"), f"route_export:{application.id}")])
            await max_client.send_message(send_id, "\n\n".join(lines), buttons)
    elif action.startswith("route_export:"):
        try:
            application_id = int(action.split(":", 1)[1])
        except ValueError:
            await max_client.send_message(send_id, "Invalid route selection.")
            return
        application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id).options(
            selectinload(Application.steps), selectinload(Application.documents).joinedload(ApplicationDocument.document),
            joinedload(Application.program).joinedload(Program.university),
        ))
        if application:
            content = render_application_checklist(application, locale)
            await max_client.send_file(send_id, f"admission-checklist-{application.id}.txt", content, tr(locale, "checklist_caption"))
    elif action.startswith("doc_ready:"):
        try:
            _, app_id, document_id = action.split(":", 2)
            application = _owned_application(db, int(app_id), user.id)
            item = next((doc for doc in application.documents if doc.id == int(document_id)), None)
        except (ValueError, HTTPException):
            item = None
            application = None
        if item and application:
            item.status = "ready"
            db.commit()
            await max_client.send_message(send_id, "Документ отмечен как готовый." if locale == "ru" else "Document marked as ready.", [[_button(tr(locale, "open_route"), f"route:{application.id}")]])
    elif action.startswith(("confirm_step:", "confirm_step_yes:")):
        parts = action.split(":")
        try:
            application_id = int(parts[1])
            step_id = int(parts[2]) if len(parts) > 2 else None
        except (ValueError, IndexError):
            await max_client.send_message(send_id, "Invalid step selection.")
            return
        application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id).options(selectinload(Application.steps), joinedload(Application.program).joinedload(Program.university)))
        if application:
            step = next((s for s in application.steps if s.id == step_id), None) if step_id is not None else next((s for s in application.steps if s.status != "completed"), None)
            if step and payload and payload.startswith(f"confirm_step_yes:{application.id}:") and step.status != "completed":
                step.status = "completed"
                if all(item.status == "completed" for item in application.steps):
                    application.status = "completed"
                db.commit()
                done = sum(s.status == "completed" for s in application.steps)
                next_step = next((s for s in application.steps if s.status != "completed"), None)
                next_title = route_step_text(next_step.step_type, locale)[0] if next_step else tr(locale, "all_done")
                await max_client.send_message(send_id, tr(locale, "marked", done=done, count=len(application.steps), next=next_title), [[_button(tr(locale, "show_route"), f"route:{application.id}")]])
            elif step and step.status != "completed":
                step_title, _ = route_step_text(step.step_type, locale)
                await max_client.send_message(send_id, tr(locale, "confirm_step", step=step_title), [[_button(tr(locale, "confirm_yes"), f"confirm_step_yes:{application.id}:{step.id}"), _button(tr(locale, "no"), f"route:{application.id}")]])
    elif text and text.strip():
        try:
            response = await answer_question(db, text.strip(), locale)
            sources = "\n".join(response["sources"])
            source_label = "Источники" if locale == "ru" else {"fr": "Sources", "es": "Fuentes"}.get(locale, "Sources")
            await max_client.send_message(send_id, response["answer"] + (f"\n\n{source_label}:\n{sources}" if sources else ""))
        except (httpx.HTTPError, KeyError, IndexError, TypeError):
            await max_client.send_message(send_id, "I could not confirm that from official sources. Please check the university admissions office.")
    elif user.state == "profile_complete":
        await max_client.send_message(send_id, tr(locale, "continue"), [[_button(tr(locale, "show_programs"), "recommendations")]])
    else:
        await max_client.send_message(send_id, tr(locale, "start_hint"))


async def handle_max_update(update: dict, db: Session) -> None:
    event_key = hashlib.sha256(json.dumps(update, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if db.scalar(select(ProcessedUpdate.id).where(ProcessedUpdate.event_key == event_key)):
        return
    user_id, _, _ = _user_from_update(update)
    try:
        parsed_user_id = int(user_id) if user_id else None
    except (TypeError, ValueError):
        parsed_user_id = None
    user = db.scalar(select(User).where(User.max_user_id == parsed_user_id)) if parsed_user_id is not None else None
    previous_state = user.state if user else None
    callback = update.get("callback") or {}
    callback_id = callback.get("callback_id") if update.get("update_type") == "message_callback" else None
    callback_token = callback_id_context.set(callback_id) if isinstance(callback_id, str) and callback_id else None
    try:
        await _handle_max_update(update, db)
    except Exception:
        # State changes are committed before sending a reply. Restore the prior
        # dialogue state so a retried MAX event can be processed correctly.
        if parsed_user_id is not None and previous_state is not None:
            current_user = db.scalar(select(User).where(User.max_user_id == parsed_user_id))
            if current_user:
                current_user.state = previous_state
                db.commit()
        raise
    finally:
        if callback_token is not None:
            callback_id_context.reset(callback_token)
    db.add(ProcessedUpdate(event_key=event_key))
    try:
        db.commit()
    except Exception:
        db.rollback()
        # A concurrent retry may have stored this same event first.
        if not db.scalar(select(ProcessedUpdate.id).where(ProcessedUpdate.event_key == event_key)):
            raise


async def show_recommendations(user: User, db: Session, send_id: int | None = None) -> None:
    locale = user.ui_language if user.ui_language in LANGUAGES else "en"
    results = recommendations(db, user)[:6]
    if not results:
        alternatives = recommendations(db, user, ignore_language=True)
        available_languages = sorted({program.language for program, _, _ in alternatives})
        if alternatives and user.language not in available_languages:
            buttons = [[_button(tr(locale, f"show_{language}_programs"), f"recommendations:language:{language}")] for language in available_languages]
            await max_client.send_message(send_id or user.max_user_id, tr(locale, "no_language_results", requested_language=tr(locale, user.language or "unknown")), buttons)
        else:
            await max_client.send_message(send_id or user.max_user_id, tr(locale, "no_results"))
        return
    text_lines = [tr(locale, "recommendations")]
    buttons = []
    for program, matched, _ in results:
        tuition = f"{program.tuition:,.0f} {program.currency}" if program.tuition is not None else tr(locale, "price_unknown")
        housing = tr(locale, "housing_yes" if program.dormitory else "housing_no") if program.dormitory_confirmed else tr(locale, "not_confirmed")
        criterion_count = len(matched) + len(_)
        unknown_count = len(CRITERIA) - criterion_count
        match_text = tr(locale, 'match', matched=len(matched), total=criterion_count)
        if unknown_count:
            match_text += f"; {tr(locale, 'unknown_criteria', count=unknown_count)}"
        text_lines.append(f"\n{program.university.short_name} — {program.name}\n{match_text} | {tuition} | {tr(locale, 'housing_label')}: {housing}")
        buttons.append([_button(tr(locale, "open", university=program.university.short_name), f"program:{program.id}")])
    if len(results) >= 2:
        buttons.append([_button(tr(locale, "compare"), "compare:" + ",".join(str(item[0].id) for item in results[:3]))])
    await max_client.send_message(send_id or user.max_user_id, "\n".join(text_lines), buttons)


@app.post("/webhook/max")
async def max_webhook(request: Request, x_max_bot_api_secret: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
    if settings.max_webhook_secret and not hmac.compare_digest(x_max_bot_api_secret or "", settings.max_webhook_secret):
        raise HTTPException(401, "Invalid webhook secret")
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_UPDATE_MAX_BYTES:
            raise HTTPException(413, "MAX update is too large")
        body.extend(chunk)
    try:
        update = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "Invalid JSON") from exc
    if not isinstance(update, dict):
        raise HTTPException(400, "MAX update must be a JSON object")
    await handle_max_update(update, db)
    return {"ok": True}


@app.post("/max/subscribe")
async def subscribe_max() -> dict:
    if not settings.webhook_public_url:
        raise HTTPException(400, "WEBHOOK_PUBLIC_URL is not configured")
    return await max_client.subscribe(settings.webhook_public_url, settings.max_webhook_secret)


@app.post("/max/commands")
async def configure_max_commands() -> dict:
    commands = [
        {"name": "start", "description": "Начать подбор программы"},
        {"name": "help", "description": "Как работает бот"},
        {"name": "programs", "description": "Показать подходящие программы"},
        {"name": "applications", "description": "Мои поступления"},
        {"name": "language", "description": "Язык интерфейса"},
        {"name": "reset", "description": "Заполнить профиль заново"},
    ]
    return await max_client.set_commands(commands)
