"""
Database session factory and init.
"""
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from store.models import Base

DB_PATH = Path(__file__).parent / "deals.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(ENGINE)
    _run_migrations()


def _is_duplicate_column_error(error: OperationalError) -> bool:
    """
    Best-effort detection for 'column already exists' errors on SQLite.
    Falls back to string matching on the underlying DB error message.
    """
    message = ""
    if getattr(error, "orig", None) is not None:
        # SQLite error string is usually in orig.args[0]
        orig = error.orig
        if getattr(orig, "args", None):
            message = str(orig.args[0])
        else:
            message = str(orig)
    else:
        message = str(error)
    message = message.lower()
    return "duplicate column" in message or "already exists" in message


def _migrate_financing_benefit() -> None:
    """C-03: Add financing_benefit column if missing (SQLite)."""
    with ENGINE.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE deals ADD COLUMN financing_benefit REAL DEFAULT 0"))
            conn.commit()
        except OperationalError as e:
            if not _is_duplicate_column_error(e):
                raise


def _migrate_carrier_columns() -> None:
    """E-03: Add carrier columns if missing (SQLite)."""
    cols = [
        ("monthly_payment", "REAL"),
        ("term_months", "INTEGER"),
        ("lock_in_penalty", "REAL"),
    ]
    with ENGINE.connect() as conn:
        for name, col_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE deals ADD COLUMN {name} {col_type}"))
                conn.commit()
            except OperationalError as e:
                if not _is_duplicate_column_error(e):
                    raise


def _run_migrations() -> None:
    _migrate_financing_benefit()
    _migrate_carrier_columns()


def get_session() -> Session:
    SessionLocal = sessionmaker(bind=ENGINE)
    return SessionLocal()

