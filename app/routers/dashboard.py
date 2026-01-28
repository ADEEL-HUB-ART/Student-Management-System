"""Dashboard and analytics routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.core.security import get_current_user, calculate_grade_point

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get dashboard statistics."""
    total_students = db.query(models.Student).count()
    total_departments = db.query(models.Department).count()
    total_subjects = db.query(models.Subject).count()
    
    paid_fees = db.query(models.Fee).filter(models.Fee.status == "paid").count()
    unpaid_fees = db.query(models.Fee).filter(models.Fee.status != "paid").count()
    
    cleared_students = db.query(models.Clearance).filter(
        models.Clearance.library_clearance == True,
        models.Clearance.finance_clearance == True,
        models.Clearance.hostel_clearance == True,
        models.Clearance.department_clearance == True
    ).count()
    
    not_cleared_students = db.query(models.Student).count() - cleared_students
    
    # Average GPA
    results = db.query(models.Result).all()
    if results:
        total_points = sum(calculate_grade_point(r.total_marks) for r in results)
        avg_gpa = round(total_points / len(results), 2)
    else:
        avg_gpa = 0.0
    
    return {
        "total_students": total_students,
        "total_departments": total_departments,
        "total_subjects": total_subjects,
        "fees": {
            "paid": paid_fees,
            "unpaid": unpaid_fees
        },
        "clearance": {
            "cleared_students": cleared_students,
            "not_cleared_students": not_cleared_students
        },
        "average_gpa": avg_gpa
    }


@router.get("/teachers/")
def get_teachers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get unique list of teachers from subjects."""
    subjects = db.query(models.Subject).all()
    teachers = {}
    
    for s in subjects:
        if s.teacher not in teachers:
            teachers[s.teacher] = {
                "name": s.teacher,
                "subjects": [],
                "departments": set()
            }
        teachers[s.teacher]["subjects"].append(s.name)
        teachers[s.teacher]["departments"].add(s.department_id)
    
    return [
        {
            "name": t["name"],
            "subjects": t["subjects"],
            "departments": list(t["departments"]),
            "subject_count": len(t["subjects"])
        }
        for t in teachers.values()
    ]
