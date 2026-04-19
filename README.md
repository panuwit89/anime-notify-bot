# 🎬 Anime Notify Bot

Discord Bot สำหรับแจ้งเตือนเมื่ออนิเมะมีตอนใหม่ออกอากาศ ดึงข้อมูลจาก [AniList](https://anilist.co/) ผ่าน GraphQL API

---

## ✨ ฟีเจอร์

- แจ้งเตือนอัตโนมัติทุกครั้งที่มีตอนใหม่ออก (ตรวจสอบทุก 10 นาที)
- ค้นหาและติดตามอนิเมะด้วย Slash Commands
- ดูรายการอนิเมะที่กำลัง On Air อยู่ตอนนี้พร้อมเวลาตอนถัดไป
- ตรวจสอบว่าแต่ละเรื่องออกมากี่ตอนแล้ว
- ตั้งค่าเวลาชดเชยสำหรับอนิเมะที่ปล่อยช้ากว่า AniList
- แจ้งเตือนไปยัง channel ที่กำหนดพร้อม embed สวยงาม

---

## 📋 สิ่งที่ต้องมีก่อนติดตั้ง

- Python 3.10 ขึ้นไป
- Discord Bot Token (ดูวิธีสร้างด้านล่าง)
- เชื่อมต่ออินเทอร์เน็ต (สำหรับดึงข้อมูลจาก AniList API)

---

## 🚀 วิธีติดตั้ง

### 1. Clone โปรเจกต์

```bash
git clone https://github.com/yourusername/anime-notify-bot.git
cd anime-notify-bot
```

### 2. ติดตั้ง dependencies

```bash
pip install discord.py aiohttp apscheduler python-dotenv
```

### 3. สร้าง Discord Bot

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications)
2. กด **New Application** แล้วตั้งชื่อ Bot
3. ไปที่แท็บ **Bot** → กด **Reset Token** → คัดลอก Token ไว้
4. เปิด **Message Content Intent** และ **Server Members Intent**
5. ไปที่ **OAuth2 → URL Generator**
   - เลือก Scope: `bot` และ `applications.commands`
   - เลือก Permission: `Send Messages`, `Embed Links`, `Mention Everyone`
6. เปิด URL ที่ได้เพื่อเชิญ Bot เข้า Server

### 4. ตั้งค่าไฟล์ `.env`

คัดลอกไฟล์ตัวอย่าง แล้วใส่ Token ที่ได้มา:

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env`:

```env
DISCORD_TOKEN=ใส่_token_ของคุณตรงนี้
```

### 5. รัน Bot

```bash
python bot.py
```

ถ้าสำเร็จจะเห็นข้อความใน terminal ประมาณนี้:

```
✅ Bot เริ่มทำงาน: AnimeName#1234
📡 Sync 6 commands แล้ว
⏰ Scheduler เริ่มทำงาน (ตรวจทุก 10 นาที)
```

---

## 📁 โครงสร้างโปรเจกต์

```
anime-notify-bot/
├── bot.py               # ไฟล์หลัก ตัว Bot และ Commands
├── anime_checker.py     # ดึงข้อมูลจาก AniList GraphQL API
├── database.py          # จัดการข้อมูล subscription (JSON file)
├── subscriptions.json   # ฐานข้อมูล (สร้างอัตโนมัติเมื่อรัน)
├── .env                 # เก็บ Token (ห้าม push ขึ้น GitHub)
├── .env.example         # ตัวอย่างไฟล์ .env
├── .gitignore
└── README.md
```

---

## 🎮 คำสั่งที่ใช้ได้

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `/subscribe <ชื่อ>` | ค้นหาและติดตามอนิเมะ bot จะแจ้งเตือนใน channel นี้ |
| `/subscribe anime_id:<id>` | ติดตามอนิเมะจาก AniList ID โดยตรง |
| `/unsubscribe <id>` | ยกเลิกการติดตามอนิเมะ (ดู ID ได้จาก `/list`) |
| `/list` | ดูรายการอนิเมะที่ติดตามอยู่ทั้งหมดพร้อมเวลาตอนถัดไป |
| `/onair` | ดูอนิเมะที่กำลัง On Air อยู่ตอนนี้ (default 10 เรื่อง สูงสุด 25) |
| `/episodes <id>` | ดูว่าอนิเมะเรื่องนั้นออกมากี่ตอนแล้ว |
| `/setoffset <id> <นาที>` | ตั้งเวลาชดเชยสำหรับอนิเมะที่ปล่อยช้ากว่า AniList |

### ตัวอย่างการใช้งาน

```
# ติดตามอนิเมะโดยค้นหาชื่อ
/subscribe Demon Slayer

# ติดตามจาก ID โดยตรง
/subscribe anime_id:52991

# ดูอนิเมะที่กำลังออกอากาศ แล้วเอา ID มาใช้
/onair
/episodes 52991

# ตั้งค่าชดเชยเวลา 30 นาที (เช่น ถ้า bot แจ้งเตือนเร็วเกินไป)
/setoffset 52991 30

# ยกเลิกติดตาม
/unsubscribe 52991
```

> 💡 **Tips การค้นหา:** ใช้ชื่อภาษาอังกฤษจะแม่นกว่า และไม่จำเป็นต้องพิมพ์ชื่อเต็ม เช่น `demon` แทน `Demon Slayer` ก็ได้

---

## ⚠️ หมายเหตุสำคัญ

- **Bot Token** คือกุญแจควบคุม Bot ห้ามแชร์ให้ใคร และห้าม push ไฟล์ `.env` ขึ้น GitHub เด็ดขาด
- ถ้า Token หลุด ให้ไป Reset Token ที่ Discord Developer Portal ทันที
- Bot จะตรวจสอบตอนใหม่ทุก 10 นาที อาจมีดีเลย์จาก AniList อัปเดตข้อมูลช้า
- ข้อมูลการติดตามทั้งหมดเก็บในไฟล์ `subscriptions.json` ในเครื่อง ควร backup ไว้ด้วย

---

## 🛠️ Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [AniList GraphQL API](https://anilist.gitbook.io/anilist-apiv2-docs/) — ข้อมูลอนิเมะ
- [APScheduler](https://apscheduler.readthedocs.io/) — จัดการ cron job
- [aiohttp](https://docs.aiohttp.org/) — HTTP client แบบ async