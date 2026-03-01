"""
SQLAlchemy ORM models. Schema is source of truth.
"""
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(64))          # "samsung" | "bestbuy" | "att"
    sku: Mapped[str] = mapped_column(String(128))
    base_price: Mapped[float] = mapped_column(Float)
    trade_in_value: Mapped[float] = mapped_column(Float, default=0.0)
    perk_value: Mapped[float] = mapped_column(Float, default=0.0)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    tco: Mapped[float] = mapped_column(Float)
    pickup_available: Mapped[bool] = mapped_column(Boolean, default=False)
    urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    urgency_deadline: Mapped[str | None] = mapped_column(String(64), nullable=True)
    perks_raw: Mapped[str] = mapped_column(Text, default="")   # comma-separated
    source_url: Mapped[str] = mapped_column(Text, default="")
    raw_json: Mapped[str] = mapped_column(Text, default="")


class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(16))    # "success" | "partial" | "failed"
    sources_attempted: Mapped[int] = mapped_column(Integer, default=0)
    sources_succeeded: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

