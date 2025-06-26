"""create core tables

Revision ID: 0001_create_core_tables
Revises:
Create Date: 2025-06-26

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_create_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # company_profile
    op.create_table(
        "company_profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=120)),
        sa.Column("industry", sa.String(length=120)),
        sa.Column("country", sa.String(length=80)),
        sa.Column("exchange", sa.String(length=40)),
        sa.Column("currency", sa.String(length=10)),
        sa.Column("description", sa.Text()),
        sa.Column("employees", sa.Integer()),
        sa.Column("market_cap", sa.BigInteger()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("symbol", name="uq_company_profile_symbol"),
    )
    op.create_index(
        "ix_company_profile_symbol", "company_profile", ["symbol"], unique=True
    )

    # financial_statement
    op.create_table(
        "financial_statement",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("company_profile.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("statement_type", sa.String(length=20), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("fiscal_quarter", sa.Integer()),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_fin_stmt_company_period",
        "financial_statement",
        ["company_id", "statement_type", "period", "fiscal_year", "fiscal_quarter"],
        unique=True,
    )

    # market_data
    op.create_table(
        "market_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("company_profile.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("volume", sa.BigInteger()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_market_data_company_date",
        "market_data",
        ["company_id", "date"],
        unique=True,
    )

    # report
    op.create_table(
        "report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("company_profile.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="SET NULL")
        ),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column(
            "report_type",
            sa.String(length=50),
            nullable=False,
            server_default="executive_summary",
        ),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("file_path", sa.String(length=512)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_report_company_date", "report", ["company_id", "report_date"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_report_company_date", table_name="report")
    op.drop_table("report")

    op.drop_index("ix_market_data_company_date", table_name="market_data")
    op.drop_table("market_data")

    op.drop_index("uq_fin_stmt_company_period", table_name="financial_statement")
    op.drop_table("financial_statement")

    op.drop_index("ix_company_profile_symbol", table_name="company_profile")
    op.drop_table("company_profile")
