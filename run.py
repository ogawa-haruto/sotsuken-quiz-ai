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

log = logging.getLogger("uvicorn")  # Render の Logs に出る

def mask_url(url: str) -> str:
    """パスワードを伏せた表示にする"""
    try:
        u = make_url(url)
        return str(u.set(password="***"))
    except Exception:
        return url

def create_app() -> FastAPI:
    app = FastAPI(title="Quiz App", version="dbg-3")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 既存の API ルーター
    app.include_router(quiz_router)

    # 静的ファイル（生成画像など）
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", include_in_schema=False)
    def root_page():
        return FileResponse("index.html")

    # 起動時に DB を必ず 1 回叩いて、接続先をログ出力（dialect に合わせてクエリを変える）
    @app.on_event("startup")
    def _db_ping():
        Base.metadata.create_all(bind=engine)  # 未作成ならテーブル作成
        with engine.connect() as conn:
            dialect = engine.dialect.name  # "postgresql" / "sqlite" など
            if dialect == "postgresql":
                ver = conn.execute(text("SELECT version()")).scalar()
            elif dialect == "sqlite":
                ver = conn.execute(text("SELECT sqlite_version()")).scalar()
            else:
                ver = "unknown"
            log.info(f"[DB] dialect={dialect} url={mask_url(settings.DATABASE_URL)} version={ver}")

    # 現在の接続先を確認するデバッグ用エンドポイント
    @app.get("/_debug/db", tags=["debug"])
    def debug_db():
        u = make_url(settings.DATABASE_URL)
        return {
            "dialect": engine.dialect.name,   # "postgresql" を期待
            "host": u.host,
            "database": u.database,
            "url_masked": str(u.set(password="***")),
        }

    return app

app = create_app()
