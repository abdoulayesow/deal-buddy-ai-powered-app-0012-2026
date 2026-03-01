"""
Database session factory and init.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from store.models import Base

DB_PATH = Path(__file__).parent / "deals.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(ENGINE)


def get_session() -> Session:
    SessionLocal = sessionmaker(bind=ENGINE)
    return SessionLocal()

