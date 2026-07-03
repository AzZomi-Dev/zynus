"""
Database configuration.

This module configures the SQLAlchemy engine, session factory, and
database session lifecycle used throughout the application.

Responsibilities:
- Create the SQLAlchemy engine.
- Configure connection pooling.
- Provide managed database sessions.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

@contextmanager
def get_db():
    """
    Provide a managed database session.

    Ensures the session is always closed after use, even if an exception
    occurs.

    Yields:
        SQLAlchemy database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()