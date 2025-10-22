import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Render では Environment の DATABASE_URL が自動でここに入ります。
    ローカルでは .env から読み取ります。
    """
    DATABASE_URL: str = "sqlite:///./app.db"
    A1111_BASE_URL: str = "http://127.0.0.1:7860"
    IMAGE_DIR: str = "static/images"

    class Config:
        env_file = ".env"

# ----- ここを追加：環境変数優先で上書き -----
_env_db_url = os.getenv("DATABASE_URL")
if _env_db_url:
    print(f"[config] DATABASE_URL detected from environment: {_env_db_url}")
    settings = Settings(DATABASE_URL=_env_db_url)
else:
    print("[config] Using default/local DATABASE_URL (sqlite)")
    settings = Settings()
# --------------------------------------------
