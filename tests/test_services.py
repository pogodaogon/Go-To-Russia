from datetime import date

from app.models import Program, University, User
from app.services import field_matches, recommendations, score_program
from app.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.main import _user_from_update
from app import main as main_module
import asyncio
from app.seed import seed_database


def test_score_program_matches_daniel_profile():
    user = User(country="Nigeria", degree="bachelor", field="computer_science", language="english", budget=500000, needs_dormitory=True)
    program = Program(degree="bachelor", field="computer_science", language="english", tuition=450000, dormitory=True, dormitory_confirmed=True, currency="RUB", name="CS", source_url="https://example.com", verified_at=date.today(), admission_cycle=2027)
    matched, not_matched = score_program(user, program)
    assert len(matched) == 5
    assert not not_matched


def test_callback_uses_pressing_user_not_bot_sender():
    update = {
        "chat_id": 137918657,
        "message": {"sender": {"user_id": 495242978}},
        "callback": {"user": {"user_id": 137918657}, "payload": "degree:bachelor"},
    }
    user_id, text, payload = _user_from_update(update)
    assert user_id == 137918657
    assert payload == "degree:bachelor"


def test_real_max_callback_payload_shape_is_parsed():
    update = {
        "update_type": "message_callback",
        "callback": {
            "timestamp": 1739184000000,
            "callback_id": "CALLBACK_ID_REDACTED",
            "user": {"user_id": 54321},
            "payload": "onboard:ask_degree:bachelor",
        },
        "message": {
            "recipient": {"chat_type": "dialog", "user_id": 54321},
            "body": {"text": "Choose a degree"},
            "sender": {"user_id": 12345, "is_bot": True},
        },
    }
    user_id, text, payload = _user_from_update(update)
    assert user_id == 54321
    assert text == "Choose a degree"
    assert payload == "onboard:ask_degree:bachelor"


def test_max_callback_runs_profile_transition_and_answers_pressed_message(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sent = []

    class FakeMaxClient:
        async def send_message(self, user_id, text, buttons=None):
            from app.max_client import callback_id_context
            sent.append((user_id, text, buttons, callback_id_context.get()))

    monkeypatch.setattr(main_module, "max_client", FakeMaxClient())
    update = {
        "update_type": "message_callback",
        "callback": {
            "callback_id": "callback-test-123",
            "user": {"user_id": 54321},
            "payload": "onboard:ask_degree:bachelor",
        },
        "message": {
            "recipient": {"chat_type": "dialog", "user_id": 54321},
            "body": {"text": "Bachelor"},
            "sender": {"user_id": 12345, "is_bot": True},
        },
    }
    with Session(engine) as db:
        user = User(max_user_id=54321, state="ask_degree", ui_language="en")
        db.add(user)
        db.commit()

        asyncio.run(main_module.handle_max_update(update, db))

        db.refresh(user)
        assert user.degree == "bachelor"
        assert user.state == "ask_field"
        assert len(sent) == 1
        user_id, _, buttons, callback_id = sent[0]
        assert user_id == 54321
        assert callback_id == "callback-test-123"
        assert any(button["payload"].startswith("onboard:ask_field:") for row in buttons for button in row)


def test_ai_matches_whole_term_not_aircraft_substring():
    aircraft = Program(name="Aircraft Engineering", degree="bachelor", field="engineering", categories="aviation, aerospace engineering", language="english", source_url="https://example.com")
    computer_science = Program(name="Computer Science", degree="bachelor", field="computer_science", categories="artificial_intelligence, software_engineering", language="english", source_url="https://example.com")
    assert field_matches("computer_science", aircraft) is False
    assert field_matches("I want AI", aircraft) is False
    assert field_matches("I want AI", computer_science) is True


def test_information_security_aliases_match_curated_program():
    program = Program(name="Information Security — Computer Systems Security", degree="bachelor", field="information_security", categories="information_security, cybersecurity", language="russian", source_url="https://example.com")
    assert field_matches("Информационная безопасность", program) is True
    assert field_matches("cybersecurity", program) is True


def test_recommendations_can_find_other_language_for_opt_in_fallback():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        university = University(name="MEPhI", short_name="MEPhI", website="https://example.com")
        db.add(university)
        db.flush()
        db.add(Program(university_id=university.id, name="Computer Science", degree="bachelor", field="computer_science", language="english", source_url="https://example.com", admission_cycle=2027))
        user = User(max_user_id=1, degree="bachelor", field="computer_science", language="russian", admission_year=2027)
        db.add(user)
        db.commit()
        assert recommendations(db, user) == []
        alternatives = recommendations(db, user, ignore_language=True)
        assert len(alternatives) == 1
        assert alternatives[0][0].language == "english"
        assert "language_match" in alternatives[0][2]


def test_seeded_information_security_program_is_recommended_for_russian_profile():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_database(db)
        user = User(max_user_id=2, degree="bachelor", field="information_security", language="russian", admission_year=2027)
        db.add(user)
        db.commit()
        results = recommendations(db, user)
        assert results
        assert results[0][0].name == "Information Security — Computer Systems Security"
        assert results[0][0].tuition is None
        assert results[0][0].source_url.startswith("https://eng.mephi.ru/")
