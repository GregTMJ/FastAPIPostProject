"""
Database narratives
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"  # Connect to database

# Add an engine to use the db
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a new session for the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# To check the usage for declarative_base, you can check the documentation
Base = declarative_base()
