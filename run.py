from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.engine.url import make_url

from app.database import Base, engine
from app.config import settings
from app.routes import router as quiz_router
import os, logging

log = logging.getLogger("uvicorn")

def create_app() -> FastAPI:
    app = FastAPI(title="Quiz Image Experiment App", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    app.include_router(quiz_router)
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", include_in_schema=False)
    def root_page():
        return FileResponse("index.html")

    # 起動時：DB接続確認
    @app.on_event("startup")
    def _db_ping():
        Base.metadata.create_all(bind=engine)
        try:
            with engine.connect() as conn:
                v = conn.execute(text("SELECT version()")).scalar()
                log.info(f"[DB] Connected dialect={engine.dialect.name} version={v}")
        except Exception as e:
            log.error(f"[DB] Connection failed: {e}")

    @app.get("/_debug/db", tags=["debug"])
    def debug_db():
        u = make_url(settings.DATABASE_URL)
        return {
            "dialect": engine.dialect.name,
            "host": u.host,
            "database": u.database,
            "url_masked": str(u.set(password='***')),
        }

    return app

app = create_app()
