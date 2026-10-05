import os
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
import models
import schemas

# 1. Environment variables load karo (.env file se)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# 2. Modern Password Hashing Engine (Argon2)
password_hash = PasswordHash.recommended()

# 3. OAuth2 Scheme: FastAPI docs ko batata hai ki login URL '/login' hai
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- HELPER FUNCTIONS ---

def hash_password(password: str) -> str:
    """Plain password ko secure Argon2 hash me convert karta hai"""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check karta hai ki plain password aur hashed password match hote hain ya nahi"""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """User ke liye JWT token banata hai"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- CURRENT USER DEPENDENCY ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Har protected API call me token verify karke logged-in user nikalta hai"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# Test script (Direct run karne par check karega)
if __name__ == "__main__":
    test_pass = "mypassword123"
    hashed = hash_password(test_pass)
    print("Password Hashing Working! Sample Hash:", hashed[:30] + "...")
    print("Password Verification:", verify_password(test_pass, hashed))
