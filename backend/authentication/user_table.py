from sqlalchemy import Column, String
from .user_db import Base
from .user_db import engine
import uuid

class User (Base) :
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    username = Column (String, unique=True, index=True)
    hashed_password = Column (String)

# Create the database tables if they don't exist
User.metadata.create_all(bind=engine)
