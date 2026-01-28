"""Student routes: CRUD, GPA, CGPA calculations."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role, calculate_grade_point

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=schemas.StudentResponse)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new student (admin only)."""
    new_student = models.Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/", response_model=List[schemas.StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all students."""
    return db.query(models.Student).all()


@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific student by ID."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/{student_id}/gpa/{semester}")
def calculate_gpa(
    student_id: int,
    semester: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Calculate GPA for a student in a specific semester."""
    results = db.query(models.Result).join(models.Subject).filter(
        models.Result.student_id == student_id,
        models.Subject.semester == semester
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this semester")

    total_points = sum(calculate_grade_point(r.total_marks) for r in results)
    gpa = total_points / len(results)
    return {"GPA": round(gpa, 2)}


@router.get("/{student_id}/cgpa")
def calculate_cgpa(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Calculate cumulative GPA for a student."""
    results = db.query(models.Result).filter(
        models.Result.student_id == student_id
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    total_points = sum(calculate_grade_point(r.total_marks) for r in results)
    cgpa = total_points / len(results)
    return {"CGPA": round(cgpa, 2)}
