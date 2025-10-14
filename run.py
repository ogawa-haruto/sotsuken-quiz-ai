from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes import router as quiz_router
from app.config import settings
import os

def create_app() -> FastAPI:
    app = FastAPI(title="Quiz App", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    app.include_router(quiz_router)

    # 画像配信のため /static を公開
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app

app = create_app()
Base.metadata.create_all(bind=engine)
