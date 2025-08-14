import os
import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return "sqlite:///./pmon.db"


def _get_engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


DATABASE_URL = _get_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, **_get_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def generate_instance_id() -> str:
    return os.getenv("PMON_INSTANCE_ID") or str(uuid.uuid4())
