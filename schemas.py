from datetime import date

from pydantic import BaseModel, EmailStr

class DepartmentCreate(BaseModel):
    name: str
    hod: str

class DepartmentResponse(DepartmentCreate):
    id: int
    class Config:
        from_attributes = True

class SubjectCreate(BaseModel):
    name: str
    semester: int
    teacher: str
    department_id: int

class SubjectResponse(SubjectCreate):
    id: int
    class Config:
        from_attributes = True

class ResultCreate(BaseModel):
    student_id: int
    subject_id: int
    midterm_marks: int
    final_marks: int
    sessional_marks: int
    total_marks: int

class ResultResponse(ResultCreate):
    id: int
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    name: str
    age: int
    semester: int
    department_id: int
    email: EmailStr
    roll_no: str

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    semester: int
    department_id: int
    email: str
    roll_no: str
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class AdminCreate(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    email: str
    class Config:
        from_attributes = True

class FeeCreate(BaseModel):
    student_id: int
    semester: int
    total_fee: float
    paid_amount: float = 0.0
    payment_date: date | None = None


class FeeResponse(FeeCreate):
    id: int
    due_amount: float
    status: str


    class Config:
        from_attributes = True


class ClearanceCreate(BaseModel):
    student_id: int
    library_clearance: bool = False
    finance_clearance: bool = False
    hostel_clearance: bool = False
    department_clearance: bool = False

class ClearanceResponse(ClearanceCreate):
    id: int
    is_cleared: bool
    class Config:
        from_attributes = True


# Announcement schemas
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"  # normal, important, urgent

class AnnouncementResponse(AnnouncementCreate):
    id: int
    posted_by: str
    created_at: str
    class Config:
        from_attributes = True


# User profile schemas
class UserProfile(BaseModel):
    id: int
    email: str
    role: str
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str