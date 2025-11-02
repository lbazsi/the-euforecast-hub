from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "EU ForecastHUB API"
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    LLAMA_API_URL: str = "http://localhost:8000/mock-llama"
    GROQ_API_KEY: Optional[str] = None
    # Make CORS_ORIGINS a string to avoid JSON parsing
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert CORS_ORIGINS string to list
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Ensure it's always a list
        if not isinstance(self.CORS_ORIGINS, list):
            self.CORS_ORIGINS = [str(self.CORS_ORIGINS)]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS_ORIGINS as a list (for backward compatibility)."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in str(self.CORS_ORIGINS).split(",") if origin.strip()]

settings = Settings()