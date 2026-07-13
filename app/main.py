import os
import logging
import time
from collections import defaultdict
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

# ─── Rate limiting ma'lumotlari (middleware'dan oldin e'lon qilinadi) ─────────
_request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))


# ─── 1. Rate-limit middleware — ENG BIRINCHI qo'shiladi ──────────────────────
#
#  Starlette stack logikasi: add_middleware() va @app.middleware("http") ikkalasi
#  ham "oxirgi qo'shilgan = eng tashqi qatlam" tartibida ishlaydi.
#
#  Biz istagan tartib:
#    So'rov → rate_limit → CORSMiddleware → Route
#
#  Buning uchun rate_limit BIRINCHI, CORS IKKINCHI qo'shilishi kerak.
#  @app.middleware("http") add_middleware() ekvivalenti — shuning uchun
#  uni CORSMiddleware add_middleware() DAN OLDIN e'lon qilamiz.

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # ✅ FIX 1: OPTIONS preflight so'rovlarini o'tkazib yuborish
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.method == "POST":
        # Railway'da haqiqiy IP X-Forwarded-For headerda bo'ladi
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )

        now = time.time()
        window = 60.0

        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip] if now - t < window
        ]

        if len(_request_counts[client_ip]) >= RATE_LIMIT:
            logger.warning(f"Rate limit: {client_ip} — {RATE_LIMIT} so'rov/daqiqa oshdi")

            # ✅ FIX 2: 429 javobida CORS headerlarini qo'lda qo'shish
            # (CORSMiddleware bu javobni ko'rmaydi, shuning uchun qo'lda yozamiz)
            origin = request.headers.get("origin", "")
            headers = {}
            if origin in ALLOWED_ORIGINS:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = "true"

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Juda ko'p so'rov. Biroz kuting."},
                headers=headers,
            )

        _request_counts[client_ip].append(now)

    return await call_next(request)


# ─── 2. CORS — rate_limit'dan KEYIN qo'shiladi (stack'da ichkariroq) ─────────
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Routes ──────────────────────────────────────────────────────────────────
from app.routes import router
app.include_router(router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Eduvisa API ishlamoqda ✅"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}