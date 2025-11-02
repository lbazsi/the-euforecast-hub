from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "EU ForecastHUB API"
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    LLAMA_API_URL: str = "http://localhost:8000/mock-llama"
    GROQ_API_KEY: Optional[str] = None
    # Support multiple CORS origins (comma-separated string or list)
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle CORS_ORIGINS from environment as comma-separated string
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

settings = Settings()
