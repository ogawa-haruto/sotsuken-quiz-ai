from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# ★ echo=True でSQLをログに出す / pool_pre_ping=True で死活監視
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=True,          # ← これで SQL が Logs に出る
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
