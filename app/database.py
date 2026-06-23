import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/eduvisa_db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Ulanish uzilgan bo'lsa avtomatik qayta ulanadi
    pool_size=5,          # Parallel ulanishlar soni
    max_overflow=10,      # Qo'shimcha ulanishlar limiti
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
