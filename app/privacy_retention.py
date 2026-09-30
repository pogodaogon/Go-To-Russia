"""Erase inactive applicant records and their linked webhook idempotency hashes."""

import asyncio
from datetime import datetime, time, timedelta
import logging
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select

from .db import SessionLocal
from .models import ProcessedUpdate, User
from .privacy import INACTIVE_RETENTION_DAYS

logger = logging.getLogger("privacy_retention")
MOSCOW = ZoneInfo("Europe/Moscow")


def purge_inactive_data(now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    cutoff = now - timedelta(days=INACTIVE_RETENTION_DAYS)
    with SessionLocal() as db:
        users = db.scalars(select(User).where(User.last_activity_at < cutoff)).all()
        if not users:
            return 0
        user_ids = [user.max_user_id for user in users]
        db.execute(delete(ProcessedUpdate).where(ProcessedUpdate.max_user_id.in_(user_ids)))
        for user in users:
            db.delete(user)
        db.commit()
        return len(users)


async def privacy_retention_loop() -> None:
    while True:
        now = datetime.now(MOSCOW)
        target = datetime.combine(now.date(), time(3), tzinfo=MOSCOW)
        if target <= now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        try:
            removed = purge_inactive_data()
            if removed:
                logger.info("Removed %s inactive applicant profiles", removed)
        except Exception:
            logger.exception("Could not remove inactive applicant profiles")
