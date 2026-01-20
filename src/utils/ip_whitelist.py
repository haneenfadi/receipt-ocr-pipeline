from loguru import logger
import os


def is_ip_whitelisted(ip_address: str) -> bool:

    logger.info(f"ENV: {os.getenv("APP_ENV")}")
    if os.getenv("APP_ENV") == "dev":
        return True

    WHITELISTED_IPS = ["127.0.0.1", "192.168.1.5"]
    # WHITELISTED_IPS = ["192.168.1.99"]

    return ip_address in WHITELISTED_IPS


#     """
#     Call the /ip-access endpoint for a given IP address and return isAllowed
#     """
# import requests
    # endpoint = "api/IHaneenAdminPanel/HaneenAi-ping"
    # params = {"ipAddress": ip_address}

    # response = requests.get(f"{base_url}{endpoint}", params=params)
    # response.raise_for_status()
    # data = response.json().get("Data", {})
    # return data.get("isAllowed", False)  # default to False if missing
