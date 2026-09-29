import httpx
from pathlib import Path

from .config import get_settings


class MaxClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.max_api_base_url.rstrip("/")
        self.token = settings.max_bot_token
        ca_bundle = Path(settings.max_ca_bundle)
        self.verify = str(ca_bundle) if ca_bundle.exists() else True

    async def send_message(self, user_id: int, text: str, buttons: list[list[dict]] | None = None) -> dict | None:
        # MAX only exposes slash commands through its native command picker.
        # Keep a callback-based navigation button attached to bot replies so
        # users can open an in-chat action menu without typing commands.
        buttons = list(buttons or [])
        buttons.append([{"type": "callback", "text": "☰ Меню / Menu", "payload": "menu"}])
        if not self.token:
            # Local development mode: webhook still works and logs the outgoing message.
            print(f"[MAX MOCK -> {user_id}] {text}")
            return {"mock": True, "text": text}
        payload: dict = {"text": text}
        payload["attachments"] = [{"type": "inline_keyboard", "payload": {"buttons": buttons}}]
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.post(f"{self.base_url}/messages", params={"user_id": user_id}, headers={"Authorization": self.token}, json=payload)
            response.raise_for_status()
            return response.json()

    async def subscribe(self, public_url: str, secret: str | None = None) -> dict:
        if not self.token:
            return {"success": False, "message": "MAX_BOT_TOKEN is not configured"}
        payload = {"url": public_url, "update_types": ["message_created", "message_callback", "bot_started"]}
        if secret:
            payload["secret"] = secret
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.post(f"{self.base_url}/subscriptions", headers={"Authorization": self.token}, json=payload)
            response.raise_for_status()
            return response.json()

    async def set_commands(self, commands: list[dict]) -> dict:
        if not self.token:
            return {"commands": commands, "mock": True}
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.patch(f"{self.base_url}/me/commands", headers={"Authorization": self.token}, json={"commands": commands})
            response.raise_for_status()
            return response.json()
