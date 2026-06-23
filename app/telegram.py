import os
import json as _json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")


def _base():
    return f"https://api.telegram.org/bot{BOT_TOKEN}"


def _flag(country: str) -> str:
    return {
        "United Kingdom": "🇬🇧", "UK": "🇬🇧",
        "USA": "🇺🇸", "United States": "🇺🇸",
        "Canada": "🇨🇦", "Australia": "🇦🇺",
        "New Zealand": "🇳🇿", "Ireland": "🇮🇪",
        "Germany": "🇩🇪", "Singapore": "🇸🇬",
        "Malaysia": "🇲🇾", "Cyprus": "🇨🇾",
    }.get(country, "🌍")


def _mime(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "pdf": "application/pdf",
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "gif": "image/gif",
        "webp": "image/webp",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }.get(ext, "application/octet-stream")


async def _send_text(client, text: str) -> bool:
    resp = await client.post(
        f"{_base()}/sendMessage",
        json={"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"},
    )
    if resp.status_code != 200:
        logger.error(f"sendMessage xato {resp.status_code}: {resp.text}")
        return False
    return True


async def send_new_lead_notification(lead_id, name, phone, country, message, source) -> bool:
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return False
    flag = _flag(country or "")
    text = (
        f"🔔 <b>YANGI LEAD!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n"
        f"🌍 <b>Davlat:</b> {flag} {country or 'Koʼrsatilmagan'}\n"
        f"💬 <b>Xabar:</b> {message or '—'}\n"
        f"🔗 <b>Manba:</b> {source}\n"
        f"🆔 <b>ID:</b> #{lead_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ Tezda bogʼlaning!"
    )
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as c:
            return await _send_text(c, text)
    except Exception as e:
        logger.error(f"TG lead xato: {e}")
        return False


async def send_new_booking_notification(booking_id, lead_id, name, phone, service, date, time_slot, notes) -> bool:
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return False
    text = (
        f"📅 <b>KONSULTATSIYA BAND!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n"
        f"🎓 <b>Xizmat:</b> {service}\n"
        f"📆 <b>Sana:</b> {date}\n"
        f"🕐 <b>Vaqt:</b> {time_slot}\n"
        f"📝 <b>Izoh:</b> {notes or '—'}\n"
        f"🆔 <b>Booking:</b> #{booking_id} | Lead #{lead_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Tasdiqlashni unutmang!"
    )
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as c:
            return await _send_text(c, text)
    except Exception as e:
        logger.error(f"TG booking xato: {e}")
        return False


async def send_new_application_notification(
    application_id, name, phone, email, university,
    faculty, dob, grade_level, cert_type, cert_score,
    files: list[tuple[str, bytes]] | None = None,
) -> bool:
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return False

    cert_text = f"{cert_type} ({cert_score})" if cert_type and cert_score else (cert_type or "—")
    grade_text = f"{grade_level}-sinf" if grade_level else "—"
    file_count = len(files) if files else 0

    text = (
        f"🎓 <b>YANGI ARIZA — UNIVERSITETGA!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n"
        f"✉️ <b>Email:</b> {email or '—'}\n"
        f"🏛 <b>Universitet:</b> {university}\n"
        f"📚 <b>Fakultet:</b> {faculty}\n"
        f"🎂 <b>Tugʼilgan sana:</b> {dob or '—'}\n"
        f"🏫 <b>Sinf:</b> {grade_text}\n"
        f"📜 <b>Sertifikat:</b> {cert_text}\n"
        f"📎 <b>Hujjatlar:</b> {file_count} ta\n"
        f"🆔 <b>Ariza ID:</b> #{application_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ Tezda bogʼlaning!"
    )

    try:
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            # 1) Matn — har doim
            ok = await _send_text(client, text)
            if not ok:
                return False
            logger.info(f"Ariza #{application_id} matn yuborildi.")

            if not files:
                return True

            # 2) 1 ta fayl
            if len(files) == 1:
                fname, fcontent = files[0]
                await client.post(
                    f"{_base()}/sendDocument",
                    data={"chat_id": ADMIN_CHAT_ID},
                    files={"document": (fname, fcontent, _mime(fname))},
                )
                return True

            # 3) Ko'p fayl — media group
            media_list = []
            upload_files = {}
            for idx, (fname, fcontent) in enumerate(files):
                field = f"f{idx}"
                upload_files[field] = (fname, fcontent, _mime(fname))
                media_list.append({"type": "document", "media": f"attach://{field}"})

            r = await client.post(
                f"{_base()}/sendMediaGroup",
                data={"chat_id": ADMIN_CHAT_ID, "media": _json.dumps(media_list)},
                files=upload_files,
            )
            if r.status_code != 200:
                logger.error(f"sendMediaGroup xato: {r.text} — alohida yuborilmoqda")
                for fname, fcontent in files:
                    try:
                        await client.post(
                            f"{_base()}/sendDocument",
                            data={"chat_id": ADMIN_CHAT_ID},
                            files={"document": (fname, fcontent, _mime(fname))},
                        )
                    except Exception as fe:
                        logger.error(f"Fayl xato ({fname}): {fe}")

            logger.info(f"Ariza #{application_id} — {len(files)} fayl yuborildi.")
            return True

    except Exception as e:
        logger.error(f"TG application xato: {e}")
        return False