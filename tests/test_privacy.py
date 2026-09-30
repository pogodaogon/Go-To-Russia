import asyncio
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app import main
from app.db import Base
from app.models import Application, ApplicationStep, Deadline, ProcessedUpdate, Program, ReminderLog, University, User
from app.privacy import CONSENT_BUTTONS, NOTICE_VERSION
from app.privacy_retention import purge_inactive_data


def _database():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


def test_first_contact_shows_notice_without_creating_profile(monkeypatch):
    engine = _database()
    sent = []

    class FakeMaxClient:
        async def send_message(self, user_id, text, buttons=None):
            sent.append((user_id, text, buttons))

    monkeypatch.setattr(main, "max_client", FakeMaxClient())
    with Session(engine) as db:
        asyncio.run(main._handle_max_update({"message": {"sender": {"user_id": 101}, "body": {"text": "/start"}}}, db))
        assert db.scalar(select(User).where(User.max_user_id == 101)) is None
        assert sent and "/privacy?lang=ru" in sent[0][1]
        assert len(sent[0][2]) == 8


def test_consent_acceptance_creates_profile_and_persists_version(monkeypatch):
    engine = _database()

    class FakeMaxClient:
        async def send_message(self, user_id, text, buttons=None):
            pass

    monkeypatch.setattr(main, "max_client", FakeMaxClient())
    with Session(engine) as db:
        update = {"message": {"sender": {"user_id": 102}, "body": {"text": CONSENT_BUTTONS["en"][0]}}}
        asyncio.run(main._handle_max_update(update, db))
        user = db.scalar(select(User).where(User.max_user_id == 102))
        assert user is not None
        assert user.consent_version == NOTICE_VERSION
        assert user.consent_at is not None
        assert user.state == "ask_country"


def test_delete_command_removes_profile_and_linked_update_hashes(monkeypatch):
    engine = _database()
    sent = []

    class FakeMaxClient:
        async def send_message(self, user_id, text, buttons=None):
            sent.append(text)

    monkeypatch.setattr(main, "max_client", FakeMaxClient())
    with Session(engine) as db:
        user = User(max_user_id=103, consent_at=datetime.utcnow(), consent_version=NOTICE_VERSION)
        university = University(name="Example", short_name="EX", website="https://example.edu")
        program = Program(name="Example programme", degree="bachelor", field="engineering", language="english", source_url="https://example.edu/program", admission_cycle=2027, university=university)
        application = Application(user=user, program=program)
        application.steps.append(ApplicationStep(step_type="application", title="Apply", position=1))
        db.add_all([user, application])
        db.flush()
        deadline = Deadline(program=program, type="application", date=datetime.utcnow().date(), admission_cycle=2027, source_url="https://example.edu/deadline")
        db.add(deadline)
        db.flush()
        db.add(ReminderLog(application_id=application.id, deadline_id=deadline.id, days_before=1))
        db.add(ProcessedUpdate(event_key="a" * 64, max_user_id=103))
        db.commit()
        asyncio.run(main._handle_max_update({"message": {"sender": {"user_id": 103}, "body": {"text": "/delete_data"}}}, db))
        assert db.scalar(select(User).where(User.max_user_id == 103)) is None
        assert db.scalar(select(ProcessedUpdate).where(ProcessedUpdate.max_user_id == 103)) is None
        assert db.scalar(select(Application).where(Application.user_id == user.id)) is None
        assert db.scalar(select(ReminderLog)) is None
        assert sent


def test_expired_user_requires_current_consent_for_profile_api():
    engine = _database()
    with Session(engine) as db:
        user = User(max_user_id=104, consent_at=datetime.utcnow() - timedelta(days=1), consent_version="old-version")
        db.add(user)
        db.commit()
        with pytest.raises(HTTPException) as exc:
            main.get_profile(104, db)
        assert exc.value.status_code == 403


def test_retention_removes_inactive_profile_and_linked_hashes(monkeypatch):
    engine = _database()
    from app import privacy_retention

    monkeypatch.setattr(privacy_retention, "SessionLocal", lambda: Session(engine))
    with Session(engine) as db:
        user = User(max_user_id=105, last_activity_at=datetime.utcnow() - timedelta(days=400))
        db.add(user)
        db.add(ProcessedUpdate(event_key="b" * 64, max_user_id=105))
        db.commit()
    assert purge_inactive_data() == 1
    with Session(engine) as db:
        assert db.scalar(select(User).where(User.max_user_id == 105)) is None
        assert db.scalar(select(ProcessedUpdate).where(ProcessedUpdate.max_user_id == 105)) is None


def test_schema_migration_adds_consent_and_owner_fields_and_clears_legacy_hashes(monkeypatch):
    from app import db as db_module

    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE programs (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, created_at TIMESTAMP)"))
        connection.execute(text("CREATE TABLE universities (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE processed_updates (id INTEGER PRIMARY KEY, event_key VARCHAR(64), processed_at TIMESTAMP)"))
        connection.execute(text("INSERT INTO processed_updates (id, event_key) VALUES (1, :event)"), {"event": "c" * 64})
    monkeypatch.setattr(db_module, "engine", engine)
    db_module.migrate_schema()
    with engine.connect() as connection:
        user_columns = {row["name"] for row in db_module.inspect(engine).get_columns("users")}
        update_columns = {row["name"] for row in db_module.inspect(engine).get_columns("processed_updates")}
        assert {"consent_at", "consent_version", "last_activity_at"} <= user_columns
        assert "max_user_id" in update_columns
        assert connection.execute(text("SELECT COUNT(*) FROM processed_updates")).scalar_one() == 0
        assert connection.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='ix_processed_updates_max_user_id'")).scalar_one() == 1
