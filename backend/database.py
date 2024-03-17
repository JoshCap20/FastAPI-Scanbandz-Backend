"""Database engine and session dependency injection niceties."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from .settings.env import getenv
from .settings.config import MODE


def _engine_str(dialect: str = "postgresql+psycopg2") -> str:
    """Helper function for reading settings from environment variables to produce connection string."""
    user = getenv("POSTGRES_USER")
    password = getenv("POSTGRES_PASSWORD")
    host = getenv("POSTGRES_HOST")
    port = getenv("POSTGRES_PORT")
    database = getenv("POSTGRES_DATABASE")
    return f"{dialect}://{user}:{password}@{host}:{port}/{database}"


"""Application-level SQLAlchemy database engine."""
# if MODE == "development":
#     engine = create_engine(_engine_str(), echo=True, pool_pre_ping=True)
# else:
# Leaving so production server echos SQL queries for now
engine = create_engine(_engine_str(), pool_pre_ping=True)


def db_session():
    """Generator function offering dependency injection of SQLAlchemy Sessions."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()