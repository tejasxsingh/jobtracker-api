from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import ApplicationStatus


# auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# jobs
class JobCreate(BaseModel):
    company: str
    role: str
    url: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    notes: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    applied_date: Optional[datetime] = None


class JobUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    applied_date: Optional[datetime] = None


class JobResponse(BaseModel):
    id: int
    company: str
    role: str
    url: Optional[str]
    status: ApplicationStatus
    notes: Optional[str]
    salary_range: Optional[str]
    location: Optional[str]
    applied_date: Optional[datetime]
    last_updated: datetime
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
