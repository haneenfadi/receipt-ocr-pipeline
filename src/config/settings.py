import os
from pydantic_settings import BaseSettings
from typing import ClassVar, Dict, List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ─────── App Config ───────
    BASE_URL: str = "http://localhost:8000"

    # ─────── Security ───────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ─────── Database ───────
    DB_NAME: str = "receipts.db"

    # ─────── Constants (not part of env) ───────
    ALLOWED_MIME_TYPES: ClassVar[Dict[str, List[str]]] = {
        "image/jpeg": ["jpg", "jpeg"],
        "image/png": ["png"]
    }


settings = Settings()
