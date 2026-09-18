import os
import shutil
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

settings = get_settings()

# Prepare sqlite DB on /tmp for serverless if needed
if settings.database_url.startswith("sqlite:////tmp/cinema.db"):
    tmp_db_path = "/tmp/cinema.db"
    seed_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cinema.db")
    if not os.path.exists(tmp_db_path) and os.path.exists(seed_db_path):
        try:
            shutil.copyfile(seed_db_path, tmp_db_path)
        except Exception as e:
            print(f"Warning: could not copy seed db: {e}")

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine_kwargs = {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    **engine_kwargs,
)


if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
