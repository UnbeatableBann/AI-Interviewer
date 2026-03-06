from datetime import date as Date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InterviewType(str, Enum):  #Haven't used yet
    hr="HR"
    technical="Technical"

class ExperienceLevel(str, Enum):
    junior = "Junior"
    mid = "Mid-Level"
    senior = "Senior"
    lead = "Lead"

class JobDescription(BaseModel):
    userid: str | None = None
    jobid: str | None = None 
    jobtitle: Optional[str] = Field(
        None, title="Job Title", description="The title of the job position"
    )
    companyname: Optional[str] = Field(
        None, title="Company Name", description="The name of the company offering the job"
    )
    experiencelevel: Optional[str] = Field(
        None, title="Experience Level", description="Required experience level (e.g., Junior, Mid, Senior)"
    )
    interviewtype: Optional[str] = Field(
        None, title="Interview Type", description="Type of interview (e.g., Online, In-person)"
    )
    description: str = Field(
        ..., title="Job Description", description="Detailed description of the job role"
    )
    requirements: Optional[str] = Field(
        None, title="Requirements", description="Job requirements, skills, or qualifications"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "examples": [{
                "jobtitle": "Software Engineer",
                "companyname": "OpenAI",
                "experiencelevel": "Mid-Level",
                "interviewtype": "HR",
                "description": "We are looking for a talented engineer to join our team...",
                "requirements": "Python, FastAPI, SQL",
                }
            ]
        }
    )


class QuestionGenerateOut(BaseModel):
    jobid: str 
    questions: List[str]

class AnswerRequest(BaseModel):
    question: str = Field(
        ...,
        description="The interview question that the candidate is answering",
        example="What is polymorphism in Object-Oriented Programming?"
    )
    answer: str = Field(
        ...,
        description="The candidate's answer to the question",
        example="Polymorphism allows objects of different classes to be treated as objects of a common superclass."
    )

    model_config= ConfigDict(
        json_schema_extra = {
                "examples": [{
                    "question": "What is polymorphism in Object-Oriented Programming?",
                    "answer": "Polymorphism allows objects of different classes to be treated as objects of a common superclass."
                    }
                ]
            }
        )

class UserInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class InterviewData(BaseModel):
    userid: str
    user: Optional[UserInfo] = None
    jobid: Optional[str] = None
    jobtitle: Optional[str] = None
    experiencelevel: Optional[str] = None
    score: Optional[float] = None
    date: Optional[Date] = None  

class InterviewSummary(BaseModel):
    total_interviews: int
    todays_interviews: int

class InterviewResponse(BaseModel):
    summary: InterviewSummary
    data: List[InterviewData]