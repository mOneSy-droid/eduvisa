import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.database import engine, Base
        from app import models  # noqa
        Base.metadata.create_all(bind=engine)
        logger.info("✅ DB jadvallar tayyor.")
    except Exception as e:
        logger.error(f"⚠️ DB xato: {e}")
    yield


app = FastAPI(
    title="Eduvisa Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        os.getenv("FRONTEND_URL", "http://localhost:8080"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import router
app.include_router(router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Eduvisa API ishlamoqda ✅"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}