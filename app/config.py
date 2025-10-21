from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Render では Environment の DATABASE_URL がここに自動で入ります
    DATABASE_URL: str = "sqlite:///./app.db"  # ローカルのデフォルト
    A1111_BASE_URL: str = "http://127.0.0.1:7860"
    IMAGE_DIR: str = "static/images"

    class Config:
        env_file = ".env"  # ローカル開発用。Render では未使用でもOK

settings = Settings()
