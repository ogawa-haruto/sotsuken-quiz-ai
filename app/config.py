from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    A1111_BASE_URL: str = "http://127.0.0.1:7860"  # A1111のAPI有効化が前提
    IMAGE_DIR: str = "static/images"               # 生成画像の保存先

settings = Settings()
