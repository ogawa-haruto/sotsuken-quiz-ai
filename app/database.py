from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# External を使う場合だけ sslmode=require を強制
DATABASE_URL = os.getenv("DATABASE_URL")

# External を使う場合だけ sslmode=require を強制
connect_args = {}
if "render.com" in DATABASE_URL and "sslmode=" not in DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # 死んだコネクションを自動復活
    pool_recycle=280,         # 5分弱で再接続（アイドル切断対策）
    pool_size=3, max_overflow=2,
    connect_args=connect_args
)