import asyncio

from app import max_client as max_client_module
from app.max_client import MaxClient, callback_id_context


class FakeResponse:
    is_success = True

    def raise_for_status(self):
        return None

    def json(self):
        return {"success": True}


class FakeAsyncClient:
    calls = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse()


def test_callback_message_uses_max_answers_endpoint(monkeypatch):
    FakeAsyncClient.calls = []
    monkeypatch.setattr(max_client_module.httpx, "AsyncClient", FakeAsyncClient)
    client = MaxClient.__new__(MaxClient)
    client.base_url = "https://platform-api2.max.ru"
    client.token = "test-token"
    client.verify = True

    async def send():
        token = callback_id_context.set("callback-123")
        try:
            await client.send_message(54321, "Updated screen", [[{"type": "callback", "text": "Next", "payload": "next"}]])
        finally:
            callback_id_context.reset(token)

    asyncio.run(send())
    url, call = FakeAsyncClient.calls[0]
    assert url.endswith("/answers")
    assert call["params"] == {"callback_id": "callback-123"}
    assert call["json"]["message"]["text"] == "Updated screen"
    assert call["json"]["message"]["attachments"][0]["type"] == "inline_keyboard"


def test_regular_message_still_uses_messages_endpoint(monkeypatch):
    FakeAsyncClient.calls = []
    monkeypatch.setattr(max_client_module.httpx, "AsyncClient", FakeAsyncClient)
    client = MaxClient.__new__(MaxClient)
    client.base_url = "https://platform-api2.max.ru"
    client.token = "test-token"
    client.verify = True
    asyncio.run(client.send_message(54321, "Hello"))
    url, call = FakeAsyncClient.calls[0]
    assert url.endswith("/messages")
    assert call["params"] == {"user_id": 54321}
    assert call["json"]["text"] == "Hello"
