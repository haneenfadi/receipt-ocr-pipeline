"""Simulation helper: simple whitelist for dev/testing."""

from loguru import logger
import os


def is_ip_whitelisted(ip_address: str) -> bool:
    logger.info(f"ENV: {os.getenv('APP_ENV')}")
    if os.getenv("APP_ENV") == "dev":
        return True

    WHITELISTED_IPS = ["127.0.0.1"]
    return ip_address in WHITELISTED_IPS
