import httpx
import asyncio
from contextvars import ContextVar
from pathlib import Path
from urllib.parse import urlparse

from .config import get_settings


callback_id_context: ContextVar[str | None] = ContextVar("max_callback_id", default=None)


def _ensure_success(response: httpx.Response) -> dict:
    response.raise_for_status()
    result = response.json()
    if isinstance(result, dict) and result.get("success") is False:
        # MAX can report an application-level failure with HTTP 200. Treat it
        # as a failed delivery so webhook processing is not silently recorded
        # as complete after a rejected message or callback answer.
        detail = result.get("message")
        raise RuntimeError(f"MAX API rejected the request: {detail or 'unspecified error'}")
    return result


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
        callback_id = callback_id_context.get()
        url = f"{self.base_url}/answers" if callback_id else f"{self.base_url}/messages"
        params = {"callback_id": callback_id} if callback_id else {"user_id": user_id}
        body = {"message": payload} if callback_id else payload
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.post(url, params=params, headers={"Authorization": self.token}, json=body)
            return _ensure_success(response)

    async def send_file(self, user_id: int, filename: str, content: bytes, caption: str) -> dict | None:
        """Upload and send a small generated text file using MAX's file API."""
        if Path(filename).name != filename or not filename.endswith(".txt") or len(content) > 1024 * 1024:
            raise ValueError("Only generated .txt files up to 1 MiB can be sent")
        if not self.token:
            print(f"[MAX MOCK -> {user_id}] file={filename} bytes={len(content)} caption={caption}")
            return {"mock": True, "filename": filename, "size": len(content)}

        headers = {"Authorization": self.token, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=30, verify=self.verify) as client:
            upload_info = await client.post(f"{self.base_url}/uploads", params={"type": "file"}, headers=headers)
            upload_info.raise_for_status()
            upload_data = upload_info.json()
            upload_url = upload_data.get("url")
            if not isinstance(upload_url, str):
                raise RuntimeError("MAX did not return a file upload URL")
            parsed = urlparse(upload_url)
            if parsed.scheme != "https" or parsed.hostname not in {"fu.oneme.ru", "omu.okcdn.ru"}:
                raise RuntimeError("MAX returned an unexpected file upload host")

            uploaded = await client.post(
                upload_url,
                headers=headers,
                files={"data": (filename, content, "text/plain; charset=utf-8")},
            )
            uploaded.raise_for_status()
            media_token = uploaded.json().get("token")
            if not isinstance(media_token, str) or not media_token:
                raise RuntimeError("MAX did not return a file token")

            payload = {
                "text": caption,
                "attachments": [
                    {"type": "file", "payload": {"token": media_token}},
                    {"type": "inline_keyboard", "payload": {"buttons": [[{"type": "callback", "text": "☰ Меню / Menu", "payload": "menu"}]]}},
                ],
            }
            callback_id = callback_id_context.get()
            url = f"{self.base_url}/answers" if callback_id else f"{self.base_url}/messages"
            params = {"callback_id": callback_id} if callback_id else {"user_id": user_id}
            body = {"message": payload} if callback_id else payload
            for attempt in range(3):
                response = await client.post(url, params=params, headers=headers, json=body)
                if response.is_success:
                    return _ensure_success(response)
                if attempt < 2 and "attachment.not.ready" in response.text:
                    await asyncio.sleep(1 + attempt)
                    continue
                response.raise_for_status()

    async def subscribe(self, public_url: str, secret: str | None = None) -> dict:
        if not self.token:
            return {"success": False, "message": "MAX_BOT_TOKEN is not configured"}
        payload = {"url": public_url, "update_types": ["message_created", "message_callback", "bot_started"]}
        if secret:
            payload["secret"] = secret
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.post(f"{self.base_url}/subscriptions", headers={"Authorization": self.token}, json=payload)
            return _ensure_success(response)

    async def set_commands(self, commands: list[dict]) -> dict:
        if not self.token:
            return {"commands": commands, "mock": True}
        async with httpx.AsyncClient(timeout=20, verify=self.verify) as client:
            response = await client.patch(f"{self.base_url}/me/commands", headers={"Authorization": self.token}, json={"commands": commands})
            return _ensure_success(response)
