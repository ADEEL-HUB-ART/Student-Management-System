"""Subject routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("/", response_model=schemas.SubjectResponse)
def create_subject(
    subject: schemas.SubjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new subject (admin only)."""
    new_subject = models.Subject(**subject.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@router.get("/", response_model=List[schemas.SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all subjects."""
    return db.query(models.Subject).all()


@router.get("/{subject_id}", response_model=schemas.SubjectResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific subject by ID."""
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject
