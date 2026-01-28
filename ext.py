import hashlib
import os
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import models
from database import SessionLocal

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

token_scheme = APIKeyHeader(name="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_grade_point(marks: int):
    if marks >= 85:
        return 4.0
    elif marks >= 75:
        return 3.5
    elif marks >= 65:
        return 3.0
    elif marks >= 55:
        return 2.5
    elif marks >= 50:
        return 2.0
    else:
        return 0.0



def require_role(role: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker


def require_roles(*roles: str):
    """Require user to have one of the specified roles."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker


def get_current_user(token: str = Depends(token_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

