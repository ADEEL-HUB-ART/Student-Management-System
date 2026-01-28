"""SQLAlchemy models for the Student Management System."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hod = Column(String)
    
    students = relationship("Student", back_populates="department_rel")
    subjects = relationship("Subject", back_populates="department_rel")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    semester = Column(Integer)
    teacher = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department_rel = relationship("Department", back_populates="subjects")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    semester = Column(Integer)
    department_id = Column(Integer, ForeignKey("departments.id"))
    email = Column(String, unique=True, index=True)
    roll_no = Column(String, unique=True, index=True)
    
    department_rel = relationship("Department", back_populates="students")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    midterm_marks = Column(Integer)
    final_marks = Column(Integer)
    sessional_marks = Column(Integer)
    total_marks = Column(Integer)
    
    student_rel = relationship("Student")
    subject_rel = relationship("Subject")


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    semester = Column(Integer)
    total_fee = Column(Float)
    paid_amount = Column(Float, default=0.0)
    due_amount = Column(Float)
    payment_date = Column(Date)
    status = Column(String, default="unpaid")
    
    student_rel = relationship("Student")


class Clearance(Base):
    __tablename__ = "clearances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    library_clearance = Column(Boolean, default=False)
    finance_clearance = Column(Boolean, default=False)
    hostel_clearance = Column(Boolean, default=False)
    department_clearance = Column(Boolean, default=False)

    student_rel = relationship("Student")

    @property
    def is_cleared(self):
        return all([
            self.library_clearance,
            self.finance_clearance,
            self.hostel_clearance,
            self.department_clearance
        ])


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    priority = Column(String, default="normal")
    posted_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
