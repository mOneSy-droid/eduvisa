import os
import logging
import secrets

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Sozlamalar ────────────────────────────────────────────────────────────────
# DIQQAT: ADMIN_API_KEY albatta .env faylida o'rnatilishi shart!
# Bu kalit orqali admin paneldagi/himoyalangan endpoint'larga kirish nazorat qilinadi.
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
if not ADMIN_API_KEY:
    logger.warning(
        "⚠️ ADMIN_API_KEY .env da topilmadi! Vaqtinchalik tasodifiy kalit ishlatiladi "
        "(server qayta ishga tushganda eski kalit ishlamay qoladi). "
        "Productionda buni .env ga albatta yozing: "
        "python -c \"import secrets; print(secrets.token_hex(32))\""
    )
    ADMIN_API_KEY = secrets.token_hex(32)
    logger.warning(f"Vaqtinchalik kalit: {ADMIN_API_KEY}")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(provided_key: str = Depends(api_key_header)) -> bool:
    """
    Himoyalangan endpoint'lar uchun dependency.
    So'rovda 'X-API-Key' header to'g'ri bo'lishi kerak.
    """
    if not provided_key or not secrets.compare_digest(provided_key, ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki yo'q API key",
        )
    return True
