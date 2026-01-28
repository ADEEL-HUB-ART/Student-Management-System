"""Department routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=schemas.DepartmentResponse)
def create_department(
    department: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new department (admin only)."""
    new_dept = models.Department(**department.model_dump())
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept


@router.get("/", response_model=List[schemas.DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all departments."""
    return db.query(models.Department).all()


@router.get("/{department_id}", response_model=schemas.DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific department by ID."""
    dept = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept
