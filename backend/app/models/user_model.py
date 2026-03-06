from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import List

class UserRole(str, Enum):
    admin = "admin"
    hr = "hr"
    student = "student"

class UserDB(BaseModel):
    userid: str
    email: EmailStr
    hashedpassword: str
    role: UserRole
    name: str

class UserInfoDB(BaseModel):
    userid: str
    name: str
    email: EmailStr
    phonenumber: str
    educationlevel: str
    major: str
    workexperience: str
    graduationyear: int
    skills: List[str]

class JobDescriptionDB(BaseModel):
    userid: str
    jobid: str
    jobtitle: str
    companyname: str
    experiencelevel: str
    interviewtype: str
    description: str
    requirements: str

class EvaluationDB(BaseModel):
    jobid: str
    userid: str
    question: str
    answer: str
    score: int
