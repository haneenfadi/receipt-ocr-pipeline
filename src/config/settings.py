# src/config/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:8000"
    WHITELISTED_IPS: list[str] = ["127.0.0.1"]


settings = Settings()
