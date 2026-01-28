"""Security utilities: password hashing, JWT tokens, and dependencies."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import models


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT Token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the subject (email)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# Dependencies
def get_current_user(
    token: str = Header(...),
    db: Session = Depends(get_db)
) -> models.User:
    """Get the current authenticated user from the token header."""
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def require_role(role: str):
    """Dependency factory that requires a specific role."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker


def require_roles(*roles: str):
    """Dependency factory that requires one of multiple roles."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker


# Grade calculation
def calculate_grade_point(total_marks: int) -> float:
    """Calculate grade point from total marks."""
    if total_marks >= 85:
        return 4.0
    elif total_marks >= 75:
        return 3.5
    elif total_marks >= 65:
        return 3.0
    elif total_marks >= 55:
        return 2.5
    elif total_marks >= 50:
        return 2.0
    else:
        return 0.0
