from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"
    bot_name: str = "UniRoute Russia"
    database_url: str = "sqlite:///./admission_navigator.db"
    max_api_base_url: str = "https://platform-api2.max.ru"
    max_bot_token: str | None = None
    max_ca_bundle: str = "certs/max-ca-bundle.pem"
    max_webhook_secret: str | None = None
    api_key: str | None = None
    reviewer_api_key: str | None = None
    webhook_public_url: str | None = None
    llm_api_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    reminder_days: str = "30,7,1"
    admission_year: int = 2027
    default_currency: str = "RUB"
    data_controller_name: str = "Project team (configure before production)"
    privacy_contact: str = "Configure before production"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
