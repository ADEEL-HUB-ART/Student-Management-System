from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models, schemas
from database import engine
from ext import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
    require_roles,
    calculate_grade_point,
)

# Create tables on startup (for simple deployments / demos).
models.Base.metadata.create_all(engine)

app = FastAPI(
    title="Student Management System",
    description="Production-ready FastAPI backend for managing students, departments, subjects, results, fees, and clearance.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home_page(request: Request) -> HTMLResponse:
    """Home: dashboard-centric view (requires login via frontend)."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
def signup_page(request: Request) -> HTMLResponse:
    """Render standalone signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request) -> HTMLResponse:
    """Render standalone login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/students-page", response_class=HTMLResponse, include_in_schema=False)
def students_page(request: Request) -> HTMLResponse:
    """Students management page (add + list)."""
    return templates.TemplateResponse("students.html", {"request": request})


@app.get("/departments-page", response_class=HTMLResponse, include_in_schema=False)
def departments_page(request: Request) -> HTMLResponse:
    """Departments management page."""
    return templates.TemplateResponse("departments.html", {"request": request})


@app.get("/subjects-page", response_class=HTMLResponse, include_in_schema=False)
def subjects_page(request: Request) -> HTMLResponse:
    """Subjects management page."""
    return templates.TemplateResponse("subjects.html", {"request": request})


@app.get("/results-page", response_class=HTMLResponse, include_in_schema=False)
def results_page(request: Request) -> HTMLResponse:
    """Results management page."""
    return templates.TemplateResponse("results.html", {"request": request})


@app.get("/fees-page", response_class=HTMLResponse, include_in_schema=False)
def fees_page(request: Request) -> HTMLResponse:
    """Fees management page."""
    return templates.TemplateResponse("fees.html", {"request": request})


@app.get("/clearance-page", response_class=HTMLResponse, include_in_schema=False)
def clearance_page(request: Request) -> HTMLResponse:
    """Clearance management page."""
    return templates.TemplateResponse("clearance.html", {"request": request})


@app.get("/gpa-page", response_class=HTMLResponse, include_in_schema=False)
def gpa_page(request: Request) -> HTMLResponse:
    """GPA Calculator page."""
    return templates.TemplateResponse("gpa.html", {"request": request})


@app.get("/announcements-page", response_class=HTMLResponse, include_in_schema=False)
def announcements_page(request: Request) -> HTMLResponse:
    """Announcements page."""
    return templates.TemplateResponse("announcements.html", {"request": request})


@app.get("/teachers-page", response_class=HTMLResponse, include_in_schema=False)
def teachers_page(request: Request) -> HTMLResponse:
    """Teachers directory page."""
    return templates.TemplateResponse("teachers.html", {"request": request})


@app.get("/profile-page", response_class=HTMLResponse, include_in_schema=False)
def profile_page(request: Request) -> HTMLResponse:
    """User profile page."""
    return templates.TemplateResponse("profile.html", {"request": request})

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


@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer", "role": db_user.role}

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
                  current_user: models.User = Depends(require_role("admin"))):
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
                 current_user: models.User = Depends(require_roles("teacher", "admin"))):
    new_result = models.Result(**result.dict())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result

@app.get("/results/student/{student_id}", response_model=list[schemas.ResultResponse], tags=["Results"])
def get_student_results(student_id: int, db: Session = Depends(get_db),
                       current_user: models.User = Depends(get_current_user)):
    return db.query(models.Result).filter(models.Result.student_id == student_id).all()

@app.post("/students/", response_model=schemas.StudentResponse, tags=["Students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), 
                  current_user: models.User = Depends(require_role("admin"))):
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


# ------------------ ANNOUNCEMENTS ------------------
@app.post("/announcements/", response_model=schemas.AnnouncementResponse, tags=["Announcements"])
def create_announcement(announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db),
                       current_user: models.User = Depends(require_role("admin"))):
    new_announcement = models.Announcement(
        title=announcement.title,
        content=announcement.content,
        priority=announcement.priority,
        posted_by=current_user.email
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return {
        "id": new_announcement.id,
        "title": new_announcement.title,
        "content": new_announcement.content,
        "priority": new_announcement.priority,
        "posted_by": new_announcement.posted_by,
        "created_at": new_announcement.created_at.isoformat() if new_announcement.created_at else ""
    }


@app.get("/announcements/", tags=["Announcements"])
def get_announcements(db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    announcements = db.query(models.Announcement).order_by(models.Announcement.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority,
            "posted_by": a.posted_by,
            "created_at": a.created_at.isoformat() if a.created_at else ""
        }
        for a in announcements
    ]


@app.delete("/announcements/{announcement_id}", tags=["Announcements"])
def delete_announcement(announcement_id: int, db: Session = Depends(get_db),
                       current_user: models.User = Depends(require_role("admin"))):
    announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(announcement)
    db.commit()
    return {"message": "Announcement deleted successfully"}


# ------------------ USER PROFILE ------------------
@app.get("/profile/me", response_model=schemas.UserProfile, tags=["Profile"])
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.put("/profile/password", tags=["Profile"])
def change_password(password_data: schemas.PasswordChange, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ------------------ TEACHERS ------------------
@app.get("/teachers/", tags=["Teachers"])
def get_teachers(db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
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