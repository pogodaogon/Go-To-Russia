import asyncio

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app import reminders
from app.db import Base
from app.models import Application, Deadline, Program, University, User
from app.privacy import NOTICE_VERSION


def test_cycle_without_confirmed_deadlines_does_not_send_reminders(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sent = []

    class FakeMaxClient:
        async def send_message(self, *args, **kwargs):
            sent.append(args)

    monkeypatch.setattr(reminders, "SessionLocal", lambda: Session(engine))
    monkeypatch.setattr(reminders, "MaxClient", FakeMaxClient)
    with Session(engine) as db:
        university = University(name="Example University", short_name="EX", website="https://example.edu")
        user = User(max_user_id=3001, consent_version=NOTICE_VERSION)
        program = Program(name="Example Program", degree="bachelor", field="engineering", language="english", source_url="https://example.edu/program", admission_cycle=2027, university=university)
        application = Application(user=user, program=program)
        db.add(application)
        db.commit()
        assert db.scalar(select(func.count(Deadline.id))) == 0
    asyncio.run(reminders.send_due_reminders())
    assert sent == []
