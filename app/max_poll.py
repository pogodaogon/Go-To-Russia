"""Development runner for MAX Long Polling.

Use this when the computer has no public HTTPS endpoint. MAX permits
GET /updates for development and testing; production should use webhook.
"""

import asyncio
import logging
from pathlib import Path

import httpx

from .config import get_settings
from .db import SessionLocal
from .main import handle_max_update

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("max_poll")


async def run() -> None:
    settings = get_settings()
    if not settings.max_bot_token:
        raise RuntimeError("MAX_BOT_TOKEN is not configured")
    ca_bundle = Path(settings.max_ca_bundle)
    verify = str(ca_bundle) if ca_bundle.exists() else True
    marker: int | None = None
    params: dict[str, object] = {
        "limit": 100,
        "timeout": 30,
        "types": "message_created,message_callback,bot_started",
    }
    async with httpx.AsyncClient(base_url=settings.max_api_base_url, timeout=45, verify=verify) as client:
        print("MAX Long Polling started. Press Ctrl+C to stop.")
        while True:
            if marker is not None:
                params["marker"] = marker
            try:
                response = await client.get("/updates", params=params, headers={"Authorization": settings.max_bot_token})
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as exc:
                logger.warning("MAX updates request failed: %s", exc)
                await asyncio.sleep(2)
                continue
            updates = data.get("updates", [])
            next_marker = data.get("marker", marker)
            batch_failed = False
            for update in updates:
                try:
                    logger.info("Received update: %s", update.get("update_type"))
                    with SessionLocal() as db:
                        await handle_max_update(update, db)
                except Exception:
                    logger.exception("Failed to process MAX update; batch will be retried")
                    batch_failed = True
                    break
            if not batch_failed:
                marker = next_marker


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("MAX Long Polling stopped.")
