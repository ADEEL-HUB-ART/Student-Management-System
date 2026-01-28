"""Result routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/results", tags=["Results"])


@router.post("/", response_model=schemas.ResultResponse)
def create_result(
    result: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("teacher", "admin"))
):
    """Create a new result (teacher/admin only)."""
    new_result = models.Result(**result.model_dump())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result


@router.get("/", response_model=List[schemas.ResultResponse])
def get_results(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all results."""
    return db.query(models.Result).all()


@router.get("/student/{student_id}", response_model=List[schemas.ResultResponse])
def get_student_results(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all results for a specific student."""
    return db.query(models.Result).filter(models.Result.student_id == student_id).all()
