# Eduvisa Backend — Ishga tushirish qo'llanmasi

## Papka tuzilishi

```
eduvisa-backend/
├── app/
│   ├── __init__.py
│   ├── main.py        ← FastAPI ilovasi
│   ├── database.py    ← PostgreSQL ulanish
│   ├── models.py      ← DB jadvallari (Lead, Booking)
│   ├── schemas.py     ← Request/Response validatsiyasi
│   ├── routes.py      ← API endpointlar
│   └── telegram.py    ← Telegram bot xabarlari
├── .env               ← Sozlamalar (siz to'ldirasiz)
├── .env.example       ← Namuna
├── requirements.txt
└── README.md
```

---

## 1. PostgreSQL — Database yaratish

```bash
# PostgreSQL o'rnatilgan bo'lishi kerak
# Ubuntu/Debian:
sudo apt install postgresql -y
sudo systemctl start postgresql

# Database va user yaratish:
sudo -u postgres psql -c "CREATE DATABASE eduvisa_db;"
sudo -u postgres psql -c "CREATE USER eduvisa_user WITH PASSWORD 'kuchli_parol';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE eduvisa_db TO eduvisa_user;"
```

---

## 2. Telegram Bot sozlash

### Bot yaratish:
1. Telegramda **@BotFather** ga boring
2. `/newbot` yuboring
3. Bot nomini kiriting: `Eduvisa Admin Bot`
4. Username kiriting: `eduvisa_admin_bot`
5. **Token** ni nusxalab oling → `.env` ga joylashtiring

### Admin Chat ID olish:
1. Telegramda **@userinfobot** ga boring
2. `/start` yuboring
3. **Id:** ni nusxalab oling → `.env` ga joylashtiring

### Botni faollashtirish:
- O'z botingizga boring va `/start` yuboring (muhim!)

---

## 3. .env faylini to'ldirish

```bash
cp .env.example .env
nano .env
```

`.env` fayl namunasi:
```env
DATABASE_URL=postgresql://eduvisa_user:kuchli_parol@localhost:5432/eduvisa_db
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ADMIN_CHAT_ID=123456789
FRONTEND_URL=http://localhost:5173
```

---

## 4. Backend ishga tushirish

```bash
cd eduvisa-backend

# Virtual environment (ixtiyoriy, tavsiya etiladi)
python3 -m venv venv
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Serverni ishga tushirish
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Muvaffaqiyatli ishga tushsa:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

---

## 5. Frontend bilan ulash

`elshodconsulting` papkasida frontend allaqachon `http://localhost:8000` ga so'rov yuboradi.

Frontendni ishga tushirish:
```bash
cd elshodconsulting
bun install
bun dev
```

---

## 6. API tekshirish

Swagger UI (brauzerda oching):
```
http://localhost:8000/docs
```

### Qo'lda test (curl):

**Yangi lead:**
```bash
curl -X POST http://localhost:8000/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Abdullayev Abdulla",
    "phone": "+998901234567",
    "country_of_interest": "UK",
    "message": "Ingliz tilini o'\''rganmoqchiman",
    "source": "website"
  }'
```

**Konsultatsiya band qilish:**
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead": 1,
    "service": "Bepul konsultatsiya",
    "date": "2024-07-20",
    "time_slot": "10:00:00",
    "notes": "UK universitetlari haqida so'\''radi"
  }'
```

---

## 7. Telegram xabari qanday ko'rinadi

Yangi lead tushganda admin bunday xabar oladi:

```
🔔 YANGI ARIZA!
━━━━━━━━━━━━━━━━━━━━
👤 Ism: Abdullayev Abdulla
📞 Telefon: +998901234567
🌍 Davlat: 🇬🇧 UK
💬 Xabar: Ingliz tilini o'rganmoqchiman
🔗 Manba: website
🆔 Lead ID: #1
━━━━━━━━━━━━━━━━━━━━
⏰ Tezda bog'laning!
```

Konsultatsiya band qilinganda:
```
📅 KONSULTATSIYA BAND QILINDI!
━━━━━━━━━━━━━━━━━━━━
👤 Ism: Abdullayev Abdulla
📞 Telefon: +998901234567
🎓 Xizmat: Bepul konsultatsiya
📆 Sana: 2024-07-20
🕐 Vaqt: 10:00:00
📝 Izoh: UK universitetlari haqida so'radi
🆔 Booking ID: #1 | Lead #1
━━━━━━━━━━━━━━━━━━━━
✅ Tasdiqlashni unutmang!
```

---

## API Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/` | Server holati |
| `GET` | `/health` | Health check |
| `POST` | `/api/leads/` | Yangi lead yaratish |
| `GET` | `/api/leads/` | Barcha leadlar |
| `GET` | `/api/leads/{id}` | Bitta lead |
| `POST` | `/api/bookings/` | Konsultatsiya band qilish |
| `GET` | `/api/bookings/` | Barcha bookinglar |
| `GET` | `/docs` | Swagger UI |

---

## Xatolar va yechimlar

**`psycopg2` xato:**
```bash
sudo apt install libpq-dev python3-dev -y
pip install psycopg2-binary
```

**`Connection refused` xato:**
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**Telegram xabar kelmasa:**
- Bot tokenini tekshiring
- Admin ID ni tekshiring
- Botga `/start` yuborgansizmi?
