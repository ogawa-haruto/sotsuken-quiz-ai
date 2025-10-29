import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quiz.db")
    A1111_BASE_URL: str = os.getenv("A1111_BASE_URL", "http://127.0.0.1:7860")
    IMAGE_DIR: str = os.getenv("IMAGE_DIR", "static/images")

settings = Settings()
