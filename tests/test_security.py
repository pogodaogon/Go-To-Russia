from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.db import Base, get_db


def test_production_api_requires_key(monkeypatch):
    monkeypatch.setattr(main.settings, "app_env", "production")
    monkeypatch.setattr(main.settings, "api_key", "test-admin-key")
    client = TestClient(main.app, raise_server_exceptions=False)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers["strict-transport-security"] == "max-age=31536000"
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["cache-control"] == "no-store"
    privacy = client.get("/privacy?lang=fr")
    assert privacy.status_code == 200
    assert privacy.headers["content-security-policy"].startswith("default-src 'none'")
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


def test_reviewer_key_is_read_only_and_limited_to_catalog(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_db():
        with session_factory() as db:
            yield db

    main.app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(main.settings, "app_env", "production")
    monkeypatch.setattr(main.settings, "api_key", "a" * 32)
    monkeypatch.setattr(main.settings, "reviewer_api_key", "r" * 32)
    client = TestClient(main.app, raise_server_exceptions=False)
    try:
        assert client.get("/programs").status_code == 401
        assert client.get("/programs", headers={"X-Reviewer-API-Key": "r" * 32}).status_code == 200
        assert client.get("/applications/1", headers={"X-Reviewer-API-Key": "r" * 32}).status_code == 401
        assert client.get("/programs", headers={"X-API-Key": "a" * 32}).status_code == 200
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        engine.dispose()
