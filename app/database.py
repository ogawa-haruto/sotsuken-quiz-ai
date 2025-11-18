# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# .env を読み込む（未導入なら pip install python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()  # プロジェクト直下の .env を読む
except Exception:
    pass  # なくても落とさない

# ① 環境変数から取得。未設定なら SQLite を既定に
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./quiz.db"

# ② Render(Postgres) の URL なら sslmode=require を自動付与
if isinstance(DATABASE_URL, str) and ("render.com" in DATABASE_URL) and ("sslmode" not in DATABASE_URL):
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# ③ SQLite の時だけ connect_args を付与
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# ④ Engine / Session / Base を一度だけ定義
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ⑤ 依存性（FastAPI で使う）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
