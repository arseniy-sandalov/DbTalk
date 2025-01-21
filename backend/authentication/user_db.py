from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

SQLALCHEMY_DATABASE_URL = "sqlite:///shared/ChatUsers.db"

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
except SQLAlchemyError as e:
    raise HTTPException(status_code=500, detail=f"Error creating database engine: {str(e)}")

try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except SQLAlchemyError as e:
    raise HTTPException(status_code=500, detail=f"Error creating database session: {str(e)}")

try:
    Base = declarative_base()
except SQLAlchemyError as e:
    raise HTTPException(status_code=500, detail=f"Error initializing declarative base: {str(e)}")
