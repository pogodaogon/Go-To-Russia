import json
from pathlib import Path

from scripts.export_openapi import build_spec


ROOT = Path(__file__).resolve().parents[1]


def test_committed_openapi_matches_app_and_describes_authentication():
    committed = json.loads((ROOT / "openapi.json").read_text(encoding="utf-8"))
    generated = build_spec()
    assert committed == generated
    assert committed["openapi"].startswith("3.1.")
    assert committed["paths"]["/health"]["get"]["security"] == []
    assert committed["paths"]["/webhook/max"]["post"]["security"] == [{"MaxWebhookSecret": []}]
    assert committed["paths"]["/programs"]["get"]["security"] == [{"ApiKey": []}, {"ReviewerApiKey": []}]


def test_hackathon_api_package_has_contract_and_safe_test_fixture():
    data_api = (ROOT / "DATA-API.yaml").read_text(encoding="utf-8")
    fixture = json.loads((ROOT / "data" / "api-test-data.json").read_text(encoding="utf-8"))
    assert "openapi: 3.1.0" in data_api
    assert "x-solution-id" in data_api
    assert "x-checks:" in data_api and "expected-status: 200" in data_api
    assert "x-roles:" in data_api and "response-format: application/json" in data_api
    assert "X-API-Key" in data_api
    assert "No credentials" in fixture["notice"]
    assert all("actual API key" not in item["auth"] for item in fixture["requests"])
