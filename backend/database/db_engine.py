"""
Database Engine - PostgreSQL/MySQL Integration

SQLAlchemy-based database layer for Ada Maritime AI.
Supports PostgreSQL (recommended) and MySQL.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from ..config import get_config

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Database engine (initialized on first use)
_engine = None
_session_factory = None


def get_database_url() -> str:
    """
    Get database connection URL from configuration

    Supported formats:
    - PostgreSQL: postgresql://user:password@host:port/database
    - MySQL: mysql+pymysql://user:password@host:port/database
    - SQLite: sqlite:///path/to/database.db
    """
    config = get_config()

    # Check for database configuration
    if hasattr(config, 'database'):
        if hasattr(config.database, 'url'):
            return config.database.url

        # Build URL from components
        db_type = getattr(config.database, 'type', 'postgresql')
        user = getattr(config.database, 'user', 'ada')
        password = getattr(config.database, 'password', 'ada_password')
        host = getattr(config.database, 'host', 'localhost')
        port = getattr(config.database, 'port', 5432)
        database = getattr(config.database, 'database', 'ada_maritime')

        if db_type == 'postgresql':
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    # Default to SQLite for development
    return "sqlite:///ada_maritime.db"


def init_database(database_url: str = None, echo: bool = False) -> None:
    """
    Initialize database engine and session factory

    Args:
        database_url: Database connection URL (if None, uses config)
        echo: Enable SQL query logging
    """
    global _engine, _session_factory

    if _engine is not None:
        logger.warning("Database already initialized")
        return

    url = database_url or get_database_url()

    logger.info(f"Initializing database: {url.split('@')[-1] if '@' in url else url}")

    # Create engine with connection pooling
    _engine = create_engine(
        url,
        echo=echo,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
    )

    # Create session factory
    _session_factory = scoped_session(
        sessionmaker(
            bind=_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    )

    logger.info("Database initialized successfully")


def get_engine():
    """Get SQLAlchemy engine (initializes if needed)"""
    if _engine is None:
        init_database()
    return _engine


def get_session():
    """Get new database session"""
    if _session_factory is None:
        init_database()
    return _session_factory()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions

    Usage:
        with get_db_session() as session:
            vessel = session.query(Vessel).filter_by(name="Sea Dream").first()
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def create_all_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=get_engine())
    logger.info("All database tables created")


def drop_all_tables():
    """Drop all database tables (USE WITH CAUTION!)"""
    Base.metadata.drop_all(bind=get_engine())
    logger.warning("All database tables dropped")


def close_database():
    """Close database connections"""
    global _engine, _session_factory

    if _session_factory:
        _session_factory.remove()
        _session_factory = None

    if _engine:
        _engine.dispose()
        _engine = None

    logger.info("Database connections closed")


# Connection event listeners
@event.listens_for(_engine, "connect", once=True)
def receive_connect(dbapi_conn, connection_record):
    """Log first database connection"""
    logger.info("First database connection established")


@event.listens_for(_engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database connection close"""
    logger.debug("Database connection closed")
