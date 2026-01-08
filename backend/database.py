"""
Database connection and session management.
Production-ready with proper connection pooling and dependency injection.
Uses SQLite for development, PostgreSQL for production.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
import os

# Create Base class for models - exported for use in models.py
Base = declarative_base()

# Use SQLite for development (no PostgreSQL required)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ai_analytics.db"
)

# Connection settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Ensures proper cleanup after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

