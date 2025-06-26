"""
User database model
"""

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    """Custom user model inheriting default id column from SQLAlchemyBaseUserTable."""

    __tablename__ = "user"
