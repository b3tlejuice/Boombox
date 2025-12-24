import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Default configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '1235')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mediaflow')

# Construct connection string
# For production use with PostgreSQL:
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# For development/testing fallback if postgres is not available (Optional, strictly speaking we should stick to psql as requested)
# But strictly following the prompt: "using Qt6 and psql"
# I will stick to the postgres url.

class DatabaseManager:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        """Creates tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

    def get_session(self):
        return self.Session()

# Global instance
db_manager = DatabaseManager()
