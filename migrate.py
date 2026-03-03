import os
import sys
import sqlalchemy
from alembic.config import Config
from alembic import command
from app.config import settings

def migrate():
    """
    Laravel-style migration:
    1. Ensures the database exists (creates it if missing).
    2. Runs all pending migrations (alembic upgrade head).
    """
    db_name = settings.db.database
    connection_type = settings.db.connection.lower()
    
    # 1. Ensure Database Exists (Auto-creation)
    if connection_type == "mysql":
        # Connect to MySQL server without a specific database
        base_url = f"mysql+pymysql://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}"
        engine = sqlalchemy.create_engine(base_url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            conn.execute(sqlalchemy.text("COMMIT"))
            print(f"✅ Database '{db_name}' verified/created.")
    
    elif connection_type in ["pgsql", "postgresql", "postgres"]:
        # Postgres auto-creation requires connecting to 'postgres' system db
        base_url = f"postgresql+psycopg://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}/postgres"
        # In Postgres, CREATE DATABASE cannot be executed in a transaction block
        engine = sqlalchemy.create_engine(base_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if exists
            res = conn.execute(sqlalchemy.text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            if not res.fetchone():
                conn.execute(sqlalchemy.text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created.")
            else:
                print(f"✅ Database '{db_name}' verified.")

    # 2. Run Migrations
    print("🚀 Running migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✨ Database and tables are fully setup and up-to-date.")

if __name__ == "__main__":
    migrate()
