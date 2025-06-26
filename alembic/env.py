"""Alembic migration environment.

This script is auto-generated (analogue of `alembic init`) and wired to load the
SQLAlchemy metadata from the EPV Research Platform so that `alembic revision
--autogenerate` works out-of-the-box.

Usage:
  1. Set DATABASE_URL env var before running migrations, e.g.
     export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/epv_db"
  2. alembic upgrade head
"""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# This is the Alembic Config object, which provides access to the values within
# the .ini file in use.
config = context.config  # type: ignore

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import project models & gather metadata
# ---------------------------------------------------------------------------
from src.auth.models import Base as AuthBase  # noqa: E402  pylint: disable=wrong-import-position
from src.db.models import Base as ProjectBase  # noqa: E402  pylint: disable=wrong-import-position

# All models share the same MetaData because they inherit from the same Base
# class, so we can safely pick one of them.
target_metadata = AuthBase.metadata  # same object as ProjectBase.metadata


# ---------------------------------------------------------------------------
# Helper to get database URL
# ---------------------------------------------------------------------------

DB_URL = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
if DB_URL is None:
    raise RuntimeError(
        "DATABASE_URL env var or sqlalchemy.url in alembic.ini must be set"
    )

config.set_main_option("sqlalchemy.url", DB_URL)

# ---------------------------------------------------------------------------
# Synchronous & asynchronous migration runners
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable: AsyncEngine = engine_from_config(  # type: ignore
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
        # Convert URL to async if using asyncpg driver
    )

    async def async_main():
        async with connectable.connect() as connection:  # type: ignore[attr-defined]
            await connection.run_sync(do_run_migrations)

    asyncio.run(async_main())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()