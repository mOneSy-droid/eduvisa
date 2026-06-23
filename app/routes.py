import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.telegram import (
    send_new_lead_notification,
    send_new_booking_notification,
    send_new_application_notification,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ─── Leads ───────────────────────────────────────────────────────────────────

@router.post("/leads/", response_model=schemas.LeadResponse, status_code=201)
async def create_lead(lead_in: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = models.Lead(
        name=lead_in.name,
        phone=lead_in.phone,
        country_of_interest=lead_in.country_of_interest,
        message=lead_in.message,
        source=lead_in.source or "website",
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    try:
        await send_new_lead_notification(
            db_lead.id, db_lead.name, db_lead.phone,
            db_lead.country_of_interest, db_lead.message, db_lead.source,
        )
    except Exception as e:
        logger.error(f"TG lead: {e}")
    return db_lead


@router.get("/leads/", response_model=List[schemas.LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Lead).order_by(models.Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/leads/{lead_id}", response_model=schemas.LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead topilmadi")
    return lead


# ─── Bookings ─────────────────────────────────────────────────────────────────

@router.post("/bookings/", response_model=schemas.BookingResponse, status_code=201)
async def create_booking(booking_in: schemas.BookingCreate, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == booking_in.lead_id).first()
    if not lead:
        raise HTTPException(404, f"Lead #{booking_in.lead_id} topilmadi")
    db_booking = models.Booking(
        lead_id=booking_in.lead_id,
        service=booking_in.service or "Bepul konsultatsiya",
        date=booking_in.date,
        time_slot=booking_in.time_slot or "10:00:00",
        notes=booking_in.notes,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    try:
        await send_new_booking_notification(
            db_booking.id, lead.id, lead.name, lead.phone,
            db_booking.service, db_booking.date, db_booking.time_slot, db_booking.notes,
        )
    except Exception as e:
        logger.error(f"TG booking: {e}")
    return db_booking


@router.get("/bookings/", response_model=List[schemas.BookingResponse])
def list_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Booking).order_by(models.Booking.created_at.desc()).offset(skip).limit(limit).all()


# ─── Applications ─────────────────────────────────────────────────────────────

@router.post("/applications/", response_model=schemas.ApplicationResponse, status_code=201)
async def create_application(
    name: str = Form(...),
    phone: str = Form(...),
    university: str = Form(...),
    faculty: str = Form(...),
    email: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    grade_level: Optional[str] = Form(None),
    cert_type: Optional[str] = Form(None),
    cert_score: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    db_app = models.Application(
        name=name, phone=phone, email=email,
        university=university, faculty=faculty,
        dob=dob, grade_level=grade_level,
        cert_type=cert_type, cert_score=cert_score,
    )
    db.add(db_app)
    db.flush()

    files_for_tg: list[tuple[str, bytes]] = []
    for upload in files:
        if not upload or not upload.filename:
            continue
        content = await upload.read()
        if not content:
            continue
        db.add(models.ApplicationFile(
            application_id=db_app.id,
            filename=upload.filename,
            content_type=upload.content_type or "application/octet-stream",
            data=content,
        ))
        files_for_tg.append((upload.filename, content))

    db.commit()
    db.refresh(db_app)

    try:
        await send_new_application_notification(
            db_app.id, db_app.name, db_app.phone, db_app.email,
            db_app.university, db_app.faculty, db_app.dob,
            db_app.grade_level, db_app.cert_type, db_app.cert_score,
            files_for_tg,
        )
    except Exception as e:
        logger.error(f"TG application: {e}")

    return db_app


@router.get("/applications/", response_model=List[schemas.ApplicationResponse])
def list_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Application).order_by(models.Application.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/applications/{app_id}", response_model=schemas.ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(404, "Ariza topilmadi")
    return app


@router.get("/applications/{app_id}/files/{file_id}")
def download_file(app_id: int, file_id: int, db: Session = Depends(get_db)):
    f = db.query(models.ApplicationFile).filter(
        models.ApplicationFile.id == file_id,
        models.ApplicationFile.application_id == app_id,
    ).first()
    if not f:
        raise HTTPException(404, "Fayl topilmadi")
    return Response(
        content=f.data,
        media_type=f.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{f.filename}"'},
    )