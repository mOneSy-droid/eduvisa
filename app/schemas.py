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


# ─── Partners (hamkorlar / akkreditatsiya) ────────────────────────────────────

class PartnerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    logo_url: str = Field(..., min_length=1, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)
    category: str = Field("accreditation", max_length=50)
    order: int = 0
    is_active: bool = True


class PartnerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    logo_url: Optional[str] = Field(None, min_length=1, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = None
    is_active: Optional[bool] = None


class PartnerResponse(BaseModel):
    id: int
    name: str
    logo_url: str
    website_url: Optional[str]
    category: str
    order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── News (yangiliklar) ────────────────────────────────────────────────────────

class NewsCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_published: bool = True


class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None


class NewsResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    is_published: bool
    published_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Banner (aylanuvchi banner) ────────────────────────────────────────────────

class BannerCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    highlight: Optional[str] = Field(None, max_length=255)
    link_url: Optional[str] = Field(None, max_length=500)
    link_label: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    order: int = 0


class BannerUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=500)
    highlight: Optional[str] = Field(None, max_length=255)
    link_url: Optional[str] = Field(None, max_length=500)
    link_label: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    order: Optional[int] = None


class BannerResponse(BaseModel):
    id: int
    text: str
    highlight: Optional[str]
    link_url: Optional[str]
    link_label: Optional[str]
    is_active: bool
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Uploads (admin panelidan rasm yuklash) ────────────────────────────────────

class UploadResponse(BaseModel):
    id: int
    filename: str
    content_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True