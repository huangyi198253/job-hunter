from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "秋招助手"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./job_hunter.db"
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {"doc", "docx", "pdf", "png", "jpeg", "jpg", "mp3", "mp4"}
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    SCRAPER_INTERVAL_HOURS: int = 24
    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
