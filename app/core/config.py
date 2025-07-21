import os
from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/gemini_db"

settings = Settings()