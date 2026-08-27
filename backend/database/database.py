import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Defaults to a local SQLite file so the backend runs with zero extra
# setup. Point DATABASE_URL at Postgres (e.g.
# postgresql+psycopg2://user:pass@localhost:5432/personal_kb) for a
# production-style multi-user deployment.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SQLITE_URL = f"sqlite:///{_PROJECT_ROOT / 'personal_kb.db'}"

DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_SQLITE_URL)

_connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()