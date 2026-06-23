from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., min_length=7, max_length=30)
    country_of_interest: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = Field(None, max_length=2000)
    source: Optional[str] = Field("website", max_length=50)


class LeadResponse(BaseModel):
    id: int
    name: str
    phone: str
    country_of_interest: Optional[str]
    message: Optional[str]
    source: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    lead_id: int
    service: Optional[str] = "Bepul konsultatsiya"
    date: str
    time_slot: Optional[str] = "10:00:00"
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    lead_id: int
    service: str
    date: str
    time_slot: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationFileResponse(BaseModel):
    id: int
    filename: str
    content_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    university: str
    faculty: str
    dob: Optional[str]
    grade_level: Optional[str]
    cert_type: Optional[str]
    cert_score: Optional[str]
    created_at: datetime
    files: List[ApplicationFileResponse] = []

    class Config:
        from_attributes = True