import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Production da /docs va /redoc yashiriladi
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"


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
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # DELETE/PUT kerak emas
    allow_headers=["*"],
)

# ─── Simple rate limiting (in-memory) ────────────────────────────────────────
from collections import defaultdict
import time

_request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))  # IP ga minutiga


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Faqat POST so'rovlarni cheklash (GET admin keydan o'tadi)
    if request.method == "POST":
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0

        # 1 daqiqa ichidagi so'rovlarni saqla
        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip] if now - t < window
        ]

        if len(_request_counts[client_ip]) >= RATE_LIMIT:
            logger.warning(f"Rate limit: {client_ip} — {RATE_LIMIT} so'rov/daqiqa oshdi")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Juda ko'p so'rov. Biroz kuting."},
            )

        _request_counts[client_ip].append(now)

    return await call_next(request)


# ─── Routes ──────────────────────────────────────────────────────────────────
from app.routes import router
app.include_router(router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Eduvisa API ishlamoqda ✅"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}