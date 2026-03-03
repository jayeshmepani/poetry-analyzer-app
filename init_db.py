from app.database import init_db
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")
