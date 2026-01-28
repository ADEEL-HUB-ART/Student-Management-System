"""Pydantic schemas for request/response validation."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr


# ============== DEPARTMENT ==============
class DepartmentCreate(BaseModel):
    name: str
    hod: str


class DepartmentResponse(DepartmentCreate):
    id: int
    
    class Config:
        from_attributes = True


# ============== SUBJECT ==============
class SubjectCreate(BaseModel):
    name: str
    semester: int
    teacher: str
    department_id: int


class SubjectResponse(SubjectCreate):
    id: int
    
    class Config:
        from_attributes = True


# ============== RESULT ==============
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


# ============== STUDENT ==============
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


# ============== AUTH ==============
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


# ============== FEE ==============
class FeeCreate(BaseModel):
    student_id: int
    semester: int
    total_fee: float
    paid_amount: float = 0.0
    payment_date: Optional[date] = None


class FeeResponse(FeeCreate):
    id: int
    due_amount: float
    status: str
    
    class Config:
        from_attributes = True


# ============== CLEARANCE ==============
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


# ============== ANNOUNCEMENT ==============
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"


class AnnouncementResponse(AnnouncementCreate):
    id: int
    posted_by: str
    created_at: str
    
    class Config:
        from_attributes = True


# ============== PROFILE ==============
class UserProfile(BaseModel):
    id: int
    email: str
    role: str
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
