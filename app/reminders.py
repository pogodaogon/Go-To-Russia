"""Daily, idempotent admission deadline reminders."""

import asyncio
from datetime import date, datetime, time, timedelta
import logging
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from .config import get_settings
from .db import SessionLocal
from .max_client import MaxClient
from .models import Application, ApplicationDocument, Deadline, Program, ReminderLog

logger = logging.getLogger("admission_reminders")
MOSCOW = ZoneInfo("Europe/Moscow")


async def send_due_reminders() -> None:
    settings = get_settings()
    try:
        reminder_days = {int(day.strip()) for day in settings.reminder_days.split(",") if day.strip()}
    except ValueError:
        logger.error("REMINDER_DAYS must be a comma-separated list of integers")
        return
    today = datetime.now(MOSCOW).date()
    client = MaxClient()
    with SessionLocal() as db:
        applications = db.scalars(select(Application).where(Application.status != "completed").options(
            joinedload(Application.user), joinedload(Application.program).joinedload(Program.university),
            selectinload(Application.documents).joinedload(ApplicationDocument.document),
        )).all()
        for application in applications:
            deadlines = db.scalars(select(Deadline).where(
                Deadline.program_id == application.program_id,
                Deadline.admission_cycle == application.program.admission_cycle,
            )).all()
            for deadline in deadlines:
                remaining = (deadline.date - today).days
                if remaining not in reminder_days:
                    continue
                already_sent = db.scalar(select(ReminderLog.id).where(
                    ReminderLog.application_id == application.id,
                    ReminderLog.deadline_id == deadline.id,
                    ReminderLog.days_before == remaining,
                ))
                if already_sent:
                    continue
                pending = [item.document.name for item in application.documents if item.document.required and item.status != "ready"]
                missing = "\n".join(f"• {name}" for name in pending) or "All required documents are marked ready."
                labels = {
                    "ru": ("Напоминание о сроке", "Осталось дней", "Ещё нужно подготовить", "Открыть маршрут"),
                    "fr": ("Rappel de date limite", "Jours restants", "À préparer", "Ouvrir le parcours"),
                    "es": ("Recordatorio de fecha límite", "Días restantes", "Aún debes preparar", "Abrir la ruta"),
                    "en": ("Deadline reminder", "Days left", "Still to prepare", "Open route"),
                }.get(application.user.ui_language, ("Deadline reminder", "Days left", "Still to prepare", "Open route"))
                message = (
                    f"{labels[0]}: {application.program.university.short_name} — {application.program.name}\n"
                    f"{deadline.type}: {deadline.date.isoformat()} ({labels[1]}: {remaining}).\n"
                    f"{labels[2]}:\n{missing}\n\n{deadline.source_url}"
                )
                try:
                    await client.send_message(application.user.max_user_id, message, [[{"type": "callback", "text": labels[3], "payload": f"route:{application.id}"}]])
                except Exception:
                    logger.exception("Failed reminder for application %s", application.id)
                    continue
                db.add(ReminderLog(application_id=application.id, deadline_id=deadline.id, days_before=remaining))
                try:
                    db.commit()
                except Exception:
                    db.rollback()
                    logger.exception("Could not persist reminder delivery for application %s", application.id)


async def reminder_loop() -> None:
    while True:
        now = datetime.now(MOSCOW)
        target = datetime.combine(now.date(), time(9), tzinfo=MOSCOW)
        if target <= now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        await send_due_reminders()
