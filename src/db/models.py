from datetime import datetime, date as _date
from typing import Optional, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Float,
    BigInteger,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

# Re-use declarative Base that already powers the auth.User table so that all
# models share one metadata / migration context.
from src.auth.models import Base  # type: ignore

__all__ = [
    "CompanyProfile",
    "FinancialStatement",
    "MarketData",
    "Report",
]


class CompanyProfile(Base):
    """Static company information.

    A dedicated table so related tables can reference the internal *id* while
    querying by the more familiar *symbol*.  The *symbol* column is indexed
    and unique to guarantee fast look-ups and referential integrity.
    """

    __tablename__ = "company_profile"

    id: int = Column(Integer, primary_key=True)
    symbol: str = Column(String(10), nullable=False, unique=True, index=True)

    company_name: str = Column(String(255), nullable=False)
    sector: Optional[str] = Column(String(120))
    industry: Optional[str] = Column(String(120))
    country: Optional[str] = Column(String(80))
    exchange: Optional[str] = Column(String(40))
    currency: Optional[str] = Column(String(10))
    description: Optional[str] = Column(Text)
    employees: Optional[int] = Column(Integer)
    market_cap: Optional[int] = Column(BigInteger)

    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    financial_statements = relationship(
        "FinancialStatement", back_populates="company", cascade="all, delete-orphan"
    )
    market_data = relationship(
        "MarketData", back_populates="company", cascade="all, delete-orphan"
    )
    reports = relationship("Report", back_populates="company", cascade="all, delete-orphan")


class FinancialStatement(Base):
    """JSON-based storage for annual / quarterly statements.

    Storing the raw statement inside a JSONB column keeps the schema flexible
    while preserving relational hooks for analytics.
    """

    __tablename__ = "financial_statement"

    id: int = Column(Integer, primary_key=True)
    company_id: int = Column(
        Integer, ForeignKey("company_profile.id", ondelete="CASCADE"), nullable=False
    )

    statement_type: str = Column(String(20), nullable=False)  # income, balance, cashflow
    period: str = Column(String(10), nullable=False)  # annual, quarterly
    fiscal_year: int = Column(Integer, nullable=False)
    fiscal_quarter: Optional[int] = Column(Integer)

    data: Any = Column(JSON, nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    company = relationship("CompanyProfile", back_populates="financial_statements")

    __table_args__ = (
        # Ensure only one row per statement-type / period / year (and quarter)
        Index(
            "uq_fin_stmt_company_period",
            "company_id",
            "statement_type",
            "period",
            "fiscal_year",
            "fiscal_quarter",
            unique=True,
        ),
    )


class MarketData(Base):
    """Daily market prices and volumes."""

    __tablename__ = "market_data"

    id: int = Column(Integer, primary_key=True)
    company_id: int = Column(
        Integer, ForeignKey("company_profile.id", ondelete="CASCADE"), nullable=False
    )

    date: _date = Column(Date, nullable=False)
    price: float = Column(Float, nullable=False)
    volume: Optional[int] = Column(BigInteger)

    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    company = relationship("CompanyProfile", back_populates="market_data")

    __table_args__ = (
        Index("ix_market_data_company_date", "company_id", "date", unique=True),
    )


class Report(Base):
    """Generated research / PDF reports tied to a company & optionally a user."""

    __tablename__ = "report"

    id: int = Column(Integer, primary_key=True)

    company_id: int = Column(
        Integer, ForeignKey("company_profile.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Optional[int] = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    report_date: _date = Column(Date, nullable=False)
    report_type: str = Column(String(50), nullable=False, default="executive_summary")
    data: Any = Column(JSON, nullable=False)  # Persisted analysis snapshot / metadata
    file_path: Optional[str] = Column(String(512))

    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    company = relationship("CompanyProfile", back_populates="reports")

    __table_args__ = (
        Index("ix_report_company_date", "company_id", "report_date"),
    )