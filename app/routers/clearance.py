"""Clearance routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/clearance", tags=["Clearance"])


@router.post("/", response_model=schemas.ClearanceResponse)
def create_or_update_clearance(
    clearance: schemas.ClearanceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create or update clearance status (admin only)."""
    existing = db.query(models.Clearance).filter(
        models.Clearance.student_id == clearance.student_id
    ).first()
    
    if existing:
        existing.library_clearance = clearance.library_clearance
        existing.finance_clearance = clearance.finance_clearance
        existing.hostel_clearance = clearance.hostel_clearance
        existing.department_clearance = clearance.department_clearance
        db.commit()
        db.refresh(existing)
        return {
            **clearance.model_dump(),
            "id": existing.id,
            "is_cleared": existing.is_cleared
        }
    
    new_clearance = models.Clearance(**clearance.model_dump())
    db.add(new_clearance)
    db.commit()
    db.refresh(new_clearance)
    return {
        **clearance.model_dump(),
        "id": new_clearance.id,
        "is_cleared": new_clearance.is_cleared
    }


@router.get("/student/{student_id}", response_model=schemas.ClearanceResponse)
def get_student_clearance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get clearance status for a student."""
    clearance = db.query(models.Clearance).filter(
        models.Clearance.student_id == student_id
    ).first()
    
    if not clearance:
        raise HTTPException(status_code=404, detail="No clearance record found")
    
    return {
        "id": clearance.id,
        "student_id": clearance.student_id,
        "library_clearance": clearance.library_clearance,
        "finance_clearance": clearance.finance_clearance,
        "hostel_clearance": clearance.hostel_clearance,
        "department_clearance": clearance.department_clearance,
        "is_cleared": clearance.is_cleared
    }
