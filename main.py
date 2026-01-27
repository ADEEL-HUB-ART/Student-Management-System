import os
import hashlib
from datetime import datetime, timedelta, date
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from jose import jwt, JWTError

import models, schemas
from database import engine, SessionLocal
from ext import get_db, hash_password, verify_password, create_access_token, get_current_user, require_role, \
    calculate_grade_point

# Create tables
models.Base.metadata.create_all(engine)

app = FastAPI(title="Student Management System")




@app.post("/signup", tags=["Authentication"])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


@app.post("/login", response_model=schemas.Token,tags=["Authentication"])
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/departments/", response_model=schemas.DepartmentResponse, tags=["Departments"])
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(require_role("admin"))):
    new_department = models.Department(**department.dict())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@app.get("/departments/", response_model=list[schemas.DepartmentResponse], tags=["Departments"])
def get_departments(db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    return db.query(models.Department).all()

@app.post("/subjects/", response_model=schemas.SubjectResponse, tags=["Subjects"])
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    new_subject = models.Subject(**subject.dict())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@app.get("/subjects/", response_model=list[schemas.SubjectResponse], tags=["Subjects"])
def get_subjects(db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    return db.query(models.Subject).all()

@app.get("/subjects/department/{department_id}/semester/{semester}", response_model=list[schemas.SubjectResponse], tags=["Subjects"])
def get_subjects_by_department_semester(department_id: int, semester: int, db: Session = Depends(get_db),
                                       current_user: models.User = Depends(get_current_user)):
    return db.query(models.Subject).filter(
        models.Subject.department_id == department_id,
        models.Subject.semester == semester
    ).all()

@app.post("/results/", response_model=schemas.ResultResponse, tags=["Results"])
def create_result(result: schemas.ResultCreate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(require_role("teacher"))):
    new_result = models.Result(**result.dict())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result

@app.get("/results/student/{student_id}", response_model=list[schemas.ResultResponse], tags=["Results"])
def get_student_results(student_id: int, db: Session = Depends(get_db),
                       current_user: models.User = Depends(get_current_user)):
    return db.query(models.Result).filter(models.Result.student_id == student_id).all()

@app.post("/students/", response_model=schemas.StudentResponse,tags=["Students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), 
                  current_user: models.User = Depends(get_current_user)):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students/", response_model=list[schemas.StudentResponse],tags=["Students"])
def get_students(db: Session = Depends(get_db), 
                current_user: models.User = Depends(get_current_user)):
    return db.query(models.Student).all()

@app.get("/students/{student_id}", response_model=schemas.StudentResponse,tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.StudentResponse,tags=["Students"])
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}",tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@app.get("/students/{student_id}/gpa/{semester}", tags=["GPA"])
def calculate_gpa(student_id: int, semester: int, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):

    results = db.query(models.Result).join(models.Subject).filter(
        models.Result.student_id == student_id,
        models.Subject.semester == semester
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    total_points = 0
    total_subjects = len(results)

    for r in results:
        gp = calculate_grade_point(r.total_marks)
        total_points += gp

    gpa = round(total_points / total_subjects, 2)
    return {"student_id": student_id, "semester": semester, "GPA": gpa}



@app.get("/students/{student_id}/cgpa", tags=["GPA"])
def calculate_cgpa(student_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):

    results = db.query(models.Result).filter(
        models.Result.student_id == student_id
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    total_points = 0
    total_subjects = len(results)

    for r in results:
        gp = calculate_grade_point(r.total_marks)
        total_points += gp

    cgpa = round(total_points / total_subjects, 2)
    return {"student_id": student_id, "CGPA": cgpa}


@app.post("/fees/", response_model=schemas.FeeResponse, tags=["Fees"])
def create_fee(fee: schemas.FeeCreate, db: Session = Depends(get_db),
               current_user: models.User = Depends(require_role("admin"))):

    due = fee.total_fee - fee.paid_amount
    status = "paid" if due <= 0 else "partial" if fee.paid_amount > 0 else "unpaid"
    new_fee = models.Fee(student_id=fee.student_id,semester=fee.semester, total_fee=fee.total_fee,paid_amount=fee.paid_amount, due_amount=due,   payment_date=fee.payment_date or date.today(),status=status )
    db.add(new_fee)
    db.commit()
    db.refresh(new_fee)
    return new_fee


@app.get("/fees/student/{student_id}", response_model=list[schemas.FeeResponse], tags=["Fees"])
def get_student_fees(student_id: int, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    return db.query(models.Fee).filter(models.Fee.student_id == student_id).all()

@app.put("/fees/{fee_id}", response_model=schemas.FeeResponse, tags=["Fees"])
def update_fee(fee_id: int, paid_amount: float, db: Session = Depends(get_db),
               current_user: models.User = Depends(require_role("admin"))):
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


# ------------------ CLEARANCE ------------------
@app.post("/clearance/", response_model=schemas.ClearanceResponse, tags=["Clearance"])
def create_clearance(clearance: schemas.ClearanceCreate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(require_role("admin"))):
    new_clearance = models.Clearance(**clearance.dict())
    db.add(new_clearance)
    db.commit()
    db.refresh(new_clearance)
    return new_clearance


@app.get("/clearance/student/{student_id}", response_model=schemas.ClearanceResponse, tags=["Clearance"])
def get_student_clearance(student_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    clearance = db.query(models.Clearance).filter(models.Clearance.student_id == student_id).first()
    if not clearance:
        raise HTTPException(status_code=404, detail="Clearance not found")
    return clearance



@app.get("/students/{student_id}/results-cleared", response_model=list[schemas.ResultResponse], tags=["Results"])
def get_results_if_cleared(student_id: int, db: Session = Depends(get_db),
                           current_user: models.User = Depends(get_current_user)):
    clearance = db.query(models.Clearance).filter(models.Clearance.student_id == student_id).first()
    if not clearance or not clearance.is_cleared:
        raise HTTPException(status_code=403, detail="Student not cleared")
    return db.query(models.Result).filter(models.Result.student_id == student_id).all()



@app.get("/dashboard/", tags=["Dashboard"])
def dashboard_stats(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_role("admin"))
):
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

    # ----- Average GPA -----
    results = db.query(models.Result).all()
    if results:
        total_points = 0
        total_subjects = len(results)

        for r in results:
            gp = calculate_grade_point(r.total_marks)
            total_points += gp

        avg_gpa = round(total_points / total_subjects, 2)
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