from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from .user_table import User
from .user_db import SessionLocal
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    """
    Opens and closes a new database session for every request.
    Ensures database connection is properly handled during request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    """
    Defines the user creation model with username and password fields.
    This model is used during user registration.
    """
    username: str
    password: str

def get_user_by_username(db: Session, username: str):
    """
    Queries the database to find a user by their username.
    If the user exists, it returns the user object.
    Raises an HTTP 500 error in case of database failure.
    
    :param db: Database session
    :param username: Username to be queried
    :return: User object or None
    """
    try:
        return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while retrieving user")

def create_user(db: Session, user: UserCreate):
    """
    Hashes the user's password and stores the new user in the database.
    Rolls back the database transaction in case of failure.
    Returns a success message on successful user creation.
    
    :param db: Database session
    :param user: UserCreate object with username and password
    :return: Success message
    """
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        return "User registered successfully"
    except SQLAlchemyError:
        db.rollback()  # Rollback in case of failure
        raise HTTPException(status_code=500, detail="Database error while creating user")

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user with the given username and password.
    Checks if the username already exists before creating the user.
    Raises an HTTP 400 error if the username is already registered.
    
    :param user: UserCreate object containing username and password
    :param db: Database session
    :return: Success message or error
    """
    try:
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        return create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during registration: {str(e)}")

def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticates the user by verifying the provided username and password.
    If the username doesn't exist or the password is incorrect, it returns False.
    Raises an HTTP 500 error in case of database issues.
    
    :param username: User's username
    :param password: User's password
    :param db: Database session
    :return: User object or False
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not pwd_context.verify(password, user.hashed_password):
            return False
        return user
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error during authentication")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a JWT access token for the authenticated user.
    The token includes an expiration time based on the provided delta.
    
    :param data: User data to include in the token
    :param expires_delta: Optional timedelta for token expiration
    :return: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError:
        raise HTTPException(status_code=500, detail="Token creation error")

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates the user and generates a JWT access token.
    If the username or password is incorrect, an HTTP 401 error is raised.
    
    :param form_data: OAuth2PasswordRequestForm containing username and password
    :param db: Database session
    :return: Access token, token type, and user ID
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id  # Return the user ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")

def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verifies the JWT token and decodes the user information.
    If the token is expired or invalid, raises an HTTP 403 error.
    
    :param token: JWT token to be verified
    :return: Payload containing user information or error
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

@router.get("/verify-token/{token}")
async def verify_user_token(token: str):
    """
    Verifies if the provided token is valid.
    Returns a success message if valid, or raises an HTTP error if invalid.
    
    :param token: JWT token to be verified
    :return: Success message or error
    """
    try:
        verify_token(token=token)
        return {"message": "Token is valid"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")
