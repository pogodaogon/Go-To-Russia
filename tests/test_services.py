from datetime import date

from app.models import Program, User
from app.services import score_program
from app.main import _user_from_update


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
