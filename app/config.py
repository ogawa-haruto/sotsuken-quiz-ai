# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"  # ← デフォルト（環境変数で上書きされる）
    A1111_BASE_URL: str = "http://127.0.0.1:7860"
    IMAGE_DIR: str = "static/images"

    class Config:
        env_file = ".env"  # ローカル開発用。Renderでは環境変数を直接読む。

settings = Settings()
