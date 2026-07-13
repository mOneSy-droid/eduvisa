from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    in_progress = "in_progress"
    closed = "closed"


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False)
    country_of_interest = Column(String(100), nullable=True)
    message = Column(Text, nullable=True)
    source = Column(String(50), default="website")
    status = Column(Enum(LeadStatus), default=LeadStatus.new)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    bookings = relationship("Booking", back_populates="lead")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    service = Column(String(200), default="Bepul konsultatsiya")
    date = Column(String(20), nullable=False)
    time_slot = Column(String(20), default="10:00:00")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    lead = relationship("Lead", back_populates="bookings")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False)
    email = Column(String(150), nullable=True)
    university = Column(String(200), nullable=False)
    faculty = Column(String(200), nullable=False)
    dob = Column(String(20), nullable=True)
    grade_level = Column(String(10), nullable=True)
    cert_type = Column(String(50), nullable=True)
    cert_score = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    files = relationship("ApplicationFile", back_populates="application", cascade="all, delete-orphan")


class ApplicationFile(Base):
    __tablename__ = "application_files"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    application = relationship("Application", back_populates="files")


class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    logo_url = Column(String(500), nullable=False)
    website_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False, default="accreditation")
    order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, nullable=False, default=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False)
    highlight = Column(String(255), nullable=True)
    link_url = Column(String(500), nullable=True)
    link_label = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())