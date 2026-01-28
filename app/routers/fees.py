"""Fee routes."""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.post("/", response_model=schemas.FeeResponse)
def create_fee(
    fee: schemas.FeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new fee record (admin only)."""
    due = fee.total_fee - fee.paid_amount
    status = "paid" if due <= 0 else ("partial" if fee.paid_amount > 0 else "unpaid")
    
    new_fee = models.Fee(
        student_id=fee.student_id,
        semester=fee.semester,
        total_fee=fee.total_fee,
        paid_amount=fee.paid_amount,
        due_amount=due,
        payment_date=fee.payment_date or date.today(),
        status=status
    )
    db.add(new_fee)
    db.commit()
    db.refresh(new_fee)
    return new_fee


@router.get("/student/{student_id}", response_model=List[schemas.FeeResponse])
def get_student_fees(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all fee records for a student."""
    return db.query(models.Fee).filter(models.Fee.student_id == student_id).all()


@router.put("/{fee_id}")
def update_fee_payment(
    fee_id: int,
    paid_amount: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Update fee payment (admin only)."""
    fee = db.query(models.Fee).filter(models.Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    
    fee.paid_amount += paid_amount
    fee.due_amount = fee.total_fee - fee.paid_amount
    fee.status = "paid" if fee.due_amount <= 0 else "partial"
    fee.payment_date = date.today()
    
    db.commit()
    db.refresh(fee)
    return fee
