import sys
from alembic.config import Config
from alembic import command

def make_migration(message: str):
    """
    Equivalent to 'php artisan make:migration'
    Autogenerates a new migration script based on model changes.
    """
    if not message:
        print("❌ Please provide a migration message. Usage: python makemigration.py 'Add column X'")
        return
        
    print(f"🛠️  Generating migration: '{message}'...")
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    print(f"✅ Migration script created in alembic/versions/")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else ""
    make_migration(msg)
