from datetime import datetime, date

from sqlalchemy import String, Integer, Date, DateTime, Float, ForeignKey, UniqueConstraint, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.auth.models import Base


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(256), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(128))
    industry: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    statements = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    prices = relationship("MarketData", back_populates="company", cascade="all, delete-orphan")
    reports = relationship("ResearchReport", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CompanyProfile {self.symbol}>"


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id", ondelete="CASCADE"), index=True)

    statement_type: Mapped[str] = mapped_column(String(32))  # income, balance, cashflow
    period: Mapped[str] = mapped_column(String(16))  # annual / quarterly
    fiscal_year: Mapped[int] = mapped_column(Integer)
    fiscal_quarter: Mapped[int | None] = mapped_column(Integer)

    # Store numeric fields as JSON blob for flexibility
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship("CompanyProfile", back_populates="statements")

    __table_args__ = (
        UniqueConstraint("company_id", "statement_type", "period", "fiscal_year", "fiscal_quarter", name="uq_statement"),
        Index("ix_financial_symbol_year", "company_id", "fiscal_year"),
    )


class MarketData(Base):
    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id", ondelete="CASCADE"), index=True)

    date: Mapped[date] = mapped_column(Date, index=True)
    price: Mapped[float] = mapped_column(Float)
    volume: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship("CompanyProfile", back_populates="prices")

    __table_args__ = (Index("ix_market_symbol_date", "company_id", "date", unique=True),)


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company_profiles.id", ondelete="CASCADE"), index=True)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    report_type: Mapped[str] = mapped_column(String(32), default="executive")
    storage_path: Mapped[str | None] = mapped_column(String(512))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    company = relationship("CompanyProfile", back_populates="reports")

    __table_args__ = (Index("ix_report_symbol_date", "company_id", "generated_at"),)