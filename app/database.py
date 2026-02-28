"""
Database Configuration
PostgreSQL/MySQL/SQLite connection setup with SQLAlchemy
"""

from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from typing import Generator, Optional
from sqlalchemy.sql.sqltypes import Integer, Float, String, Text, DateTime, JSON
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./poetry_analyzer.db"
)

# Detect database type
DB_TYPE = "sqlite"
if DATABASE_URL.startswith("postgresql"):
    DB_TYPE = "postgresql"
elif DATABASE_URL.startswith("mysql"):
    DB_TYPE = "mysql"

logger.info(f"📊 Using database type: {DB_TYPE}")
logger.info(f"🔗 Database URL: {'***' if 'password' in DATABASE_URL else DATABASE_URL}")

# Create engine with appropriate configuration for each database type
try:
    if DB_TYPE == "sqlite":
        # SQLite configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
            poolclass=StaticPool,
            pool_pre_ping=True
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
    elif DB_TYPE == "mysql":
        # MySQL/MariaDB configuration
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,
            poolclass=QueuePool,
            # MySQL-specific settings
            connect_args={
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        )
        logger.info("✅ MySQL connection pool configured")
        
    elif DB_TYPE == "postgresql":
        # PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            poolclass=QueuePool
        )
        logger.info("✅ PostgreSQL connection pool configured")
        
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def _sqlite_column_type(column) -> str:
    """Map SQLAlchemy column types to SQLite-compatible column types."""
    coltype = column.type
    if isinstance(coltype, Integer):
        return "INTEGER"
    if isinstance(coltype, Float):
        return "FLOAT"
    if isinstance(coltype, String):
        return f"VARCHAR({coltype.length})" if getattr(coltype, "length", None) else "TEXT"
    if isinstance(coltype, Text):
        return "TEXT"
    if isinstance(coltype, DateTime):
        return "DATETIME"
    if isinstance(coltype, JSON):
        return "JSON"
    return "TEXT"


def _sync_sqlite_schema(model_base) -> None:
    """
    Add missing nullable columns for existing SQLite tables.
    This keeps older local databases compatible with newer models.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table in model_base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue

            existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns or column.primary_key:
                    continue

                sql_type = _sqlite_column_type(column)
                conn.execute(
                    text(f"ALTER TABLE {table.name} ADD COLUMN {column.name} {sql_type}")
                )
                logger.info(
                    f"🛠️ Added missing SQLite column '{column.name}' to '{table.name}'"
                )


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test database connection
    Returns True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            if DB_TYPE == "sqlite":
                conn.execute(text("SELECT 1"))
            elif DB_TYPE == "mysql":
                conn.execute(text("SELECT 1"))
            elif DB_TYPE == "postgresql":
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


def init_db() -> None:
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    try:
        # Test connection first
        if not test_connection():
            raise Exception("Database connection test failed")
        
        from app.models.db_models import Base as ModelBase

        # Create tables from the actual model metadata
        ModelBase.metadata.create_all(bind=engine)

        if DB_TYPE == "sqlite":
            _sync_sqlite_schema(ModelBase)

        logger.info("✅ Database tables created successfully")
        
        # Verify tables were created
        if DB_TYPE == "sqlite":
            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"📋 Tables created: {tables}")
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def drop_all_tables() -> None:
    """
    Drop all tables (use with caution!)
    Useful for development/resetting database
    """
    try:
        logger.warning("⚠️ Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        raise


def get_database_info() -> dict:
    """
    Get database information and statistics
    """
    try:
        from app.models.db_models import AnalysisResult
        
        db = SessionLocal()
        try:
            # Get total count
            total = db.query(AnalysisResult).count()
            
            # Get database size
            if DB_TYPE == "sqlite":
                import os
                db_path = DATABASE_URL.replace("sqlite:///", "")
                size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            elif DB_TYPE == "postgresql":
                result = db.execute(text("SELECT pg_database_size(current_database())"))
                size_bytes = result.scalar() or 0
            elif DB_TYPE == "mysql":
                result = db.execute(text(
                    "SELECT SUM(data_length + index_length) FROM information_schema.tables "
                    "WHERE table_schema = DATABASE()"
                ))
                size_bytes = result.scalar() or 0
            else:
                size_bytes = 0
            
            return {
                "type": DB_TYPE,
                "total_analyses": total,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "status": "connected"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")
        return {
            "type": DB_TYPE,
            "status": "error",
            "error": str(e)
        }
