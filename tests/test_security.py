from fastapi.testclient import TestClient

from app import main


def test_production_api_requires_key(monkeypatch):
    monkeypatch.setattr(main.settings, "app_env", "production")
    monkeypatch.setattr(main.settings, "api_key", "test-admin-key")
    client = TestClient(main.app, raise_server_exceptions=False)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers["strict-transport-security"] == "max-age=31536000"
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["cache-control"] == "no-store"
    denied = client.get("/openapi.json")
    assert denied.status_code == 401
    assert denied.headers["x-frame-options"] == "DENY"
    assert client.get("/openapi.json", headers={"X-API-Key": "test-admin-key"}).status_code == 200


def test_webhook_rejects_bad_secret_and_invalid_payload(monkeypatch):
    monkeypatch.setattr(main.settings, "max_webhook_secret", "test-webhook-secret")
    client = TestClient(main.app, raise_server_exceptions=False)
    assert client.post("/webhook/max", json={}, headers={"X-Max-Bot-Api-Secret": "wrong"}).status_code == 401
    headers = {"X-Max-Bot-Api-Secret": "test-webhook-secret"}
    assert client.post("/webhook/max", content=b"{", headers=headers).status_code == 400
    assert client.post("/webhook/max", content=b"x" * (main.MAX_UPDATE_MAX_BYTES + 1), headers=headers).status_code == 413
