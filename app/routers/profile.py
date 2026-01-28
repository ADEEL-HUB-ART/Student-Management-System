"""Profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=schemas.UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.put("/password")
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Change current user's password."""
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
