import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///boombox.db"

class DatabaseManager:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        try:
            Base.metadata.create_all(self.engine)
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

    def get_session(self):
        return self.Session()

db_manager = DatabaseManager()
