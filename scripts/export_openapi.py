"""Export the API contract with the production authentication rules."""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def build_spec() -> dict:
    spec = app.openapi()
    spec["openapi"] = "3.1.0"
    spec["servers"] = [{"url": "https://77-91-115-50.sslip.io", "description": "Production API"}]
    spec.setdefault("components", {}).setdefault("securitySchemes", {}).update({
        "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        "ReviewerApiKey": {"type": "apiKey", "in": "header", "name": "X-Reviewer-API-Key"},
        "MaxWebhookSecret": {"type": "apiKey", "in": "header", "name": "X-Max-Bot-Api-Secret"},
    })
    for path, methods in spec["paths"].items():
        for operation in methods.values():
            if not isinstance(operation, dict):
                continue
            if path == "/webhook/max":
                operation["security"] = [{"MaxWebhookSecret": []}]
            elif path == "/health":
                operation["security"] = []
            elif path in ("/universities", "/programs", "/comparison") or path.startswith("/programs/"):
                operation["security"] = [{"ApiKey": []}, {"ReviewerApiKey": []}]
            else:
                operation["security"] = [{"ApiKey": []}]
    return spec


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "openapi.json"
    path.write_text(json.dumps(build_spec(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
