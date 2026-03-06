from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional




class EmailRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "examples": [
                {
                    "email": "nisey45857@amcret.com"
                }
            ]
        }
    )

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str
    
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "examples": [
                {
                    "email": "nisey45857@amcret.com",
                    "otp": ""
                }
            ]
        }
    )

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "examples": [
                {
                    "email": "alice@example.com",
                    "old_password": "StrongP@ssw0rd!",
                    "new_password": "ABCDDD"
                
                }
            ]
        }
    )

class SetNewPasswordRequest(BaseModel):
    email: EmailStr
    newpassword: str 

class UserRole(str, Enum):
    hr = "hr"
    student = "student"

class UserSignUp(BaseModel):
    email: EmailStr = Field(
        ...,
        title="Email Address",
        description="The user's contact email address for authentication."
    )
    password: str = Field(
        ...,
        title="Password",
        description="A strong password for securing the account."
    )
    role: UserRole = Field(
        ...,
        title="User Role",
        description='The role of the user — either "candidate" or "hr".'
    )
    name: str = Field(
        ...,
        title="Full Name",
        description="The user's full name as they want it displayed."
    )

    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra='ignore',
        json_schema_extra={
            "examples": [
                {
                    "email": "alice@example.com",
                    "password": "StrongP@ssw0rd!",
                    "role": "student",
                    "name": "Alice Johnson"
                }
            ]
        }
    )

class UserOut(BaseModel):
    userid: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    name: str = Field(
        ...,
        title="Full Name",
        description="The user's full legal name.",
        examples=["Alice Johnson"]
    )
    email: EmailStr = Field(
        ...,
        title="Email Address",
        description="The user's contact email address.",
        examples=["alice@example.com"]
    )
    phonenumber: str = Field(
        ...,
        title="Phone Number",
        description="A valid contact number including country code.",
        examples=["+1-202-555-0173"]
    )
    educationlevel: str = Field(
        ...,
        title="Education Level",
        description="Highest completed level of education.",
        examples=["Bachelor's", "Master's"]
    )
    major: str = Field(
        ...,
        title="Major",
        description="Field of study in higher education.",
        examples=["Computer Science", "Mechanical Engineering"]
    )
    workexperience: Optional[str] = Field(
        None,
        title="Work Experience",
        description="Summary of professional experience.",
        examples=["3 years at TechCorp", None]
    )
    graduationyear: int = Field(
        ...,
        title="Graduation Year",
        description="Year of graduation from highest education level.",
        examples=[2020]
    )
    skills: List[str] = Field(
        ...,
        title="Skills",
        description="List of professional or technical skills.",
        examples=[["Python", "Data Analysis", "Machine Learning"]]
    )

    userid: str | None = None  
    
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra='ignore',
        json_schema_extra={
            "examples": [
                {
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "phonenumber": "+1-202-555-0173",
                    "educationlevel": "Bachelor's",
                    "major": "Computer Science",
                    "workexperience": "3 years at TechCorp",
                    "graduationyear": 2020,
                    "skills": ["Python", "Data Analysis", "Machine Learning"]
                }
            ]
        }
    )

class UpdateUserInfo(BaseModel):
    educationlevel: Optional[str] = Field(None, title="Education Level")
    major: Optional[str] = Field(None, title="Major")
    workexperience: Optional[str] = Field(None, title="Work Experience")
    graduationyear: Optional[int] = Field(None, title="Graduation Year")
    skills: Optional[List[str]] = Field(None, title="Skills")

    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="ignore",
        json_schema_extra={
            "examples": [
                {
                    "skills": ["Python", "FastAPI"]
                }
            ]
        }

    )