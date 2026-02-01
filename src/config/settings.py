from pydantic_settings import BaseSettings
from typing import ClassVar, Dict, List

class Settings(BaseSettings):
    
    # Here, we use localhost and 127.0.0.1 to simulate a production-like setup for learning purposes.
    
    BASE_URL: str = "http://localhost:8000"


    ALLOWED_MIME_TYPES: ClassVar[Dict[str, List[str]]] = {
        "image/jpeg": ["jpg", "jpeg"],
        "image/png": ["png"]
    }

settings = Settings()
