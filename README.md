# برنامه دسکتاپ سلامت و رشد ۳۶۵ روزه (HeightProgram Desktop)

سامانه جامع و حرفه‌ای مدیریت روزانه **ورزش، تغذیه و خواب** برای نوجوانان ۱۵ ساله.

---

### هشدارهای مهم پزشکی و ایمنی (Safety Guidelines):
- **«این برنامه افزایش قد مشخصی را تضمین نمیکند. هدف آن ارتقای سلامت عمومی، آمادگی جسمانی، تغذیه کافی، خواب منظم و پشتیبانی از پتانسیل طبیعی رشد است.»**
- **«درد تیز یا غیرعادی در مفاصل یا ستون فقرات = توقف فوری تمرین.»**
- **«هورمون رشد یا مکمل افزایش قد بدون تجویز پزشک فوق تخصص غدد نباید مصرف شود.»**
- **«خواب عمیق و تغذیه متوازن در دوران رشد بالاترین اهمیت فیزیولوژیک را دارند.»**

---

## ۱. مشخصات کاربر و تجهیزات
- **سن:** ۱۵ سال
- **قد:** ۱۷۲ سانتیمتر | **وزن:** ۴۵ کیلوگرم
- **تجهیزات ورزشی تحت پوشش:**
  1. تردمیل (Treadmill)
  2. بارفیکس (Pull-up Bar)
  3. توپ بزرگ ورزشی (Swiss / Gym Ball)
  4. کش ورزشی مقاومتی (Resistance Bands)
  5. دستگاه مسگری (Twister Disk)

---

## ۲. دستورالعمل نصب و راه‌اندازی در ویندوز (Windows)

### گام اول: نصب Python
1. به سایت رسمی [python.org/downloads](https://www.python.org/downloads/) مراجعه کرده و آخرین نسخه پایتون (۳.۱۰ یا جدیدتر) را دانلود کنید.
2. هنگام نصب، حتماً گزینه **"Add Python to PATH"** را تیک بزنید.

### گام دوم: نصب کتابخانه‌های وابسته (Dependencies)
پوشه پروژه را در CMD یا PowerShell باز کرده و دستور زیر را اجرا کنید:
```bash
pip install -r requirements.txt
```
یا به صورت دستی:
```bash
pip install customtkinter pillow pygame
```

### گام سوم: اجرای برنامه
```bash
python main.py
```

---

## ۳. روش افزودن فایل‌های GIF و تصاویر
- **ویدیوها و GIFهای تمرین:** فایل‌های گیف هر حرکت را داخل مسیر `assets/exercises/` با نام‌های استاندارد قرار دهید:
  - `assets/exercises/pushup.gif`
  - `assets/exercises/pullup.gif`
  - `assets/exercises/squat.gif`
  - `assets/exercises/dead_hang.gif`
- **عکس‌های غذاها:** تصاویر باکیفیت وعده‌ها را در مسیر `assets/foods/` قرار دهید:
  - `assets/foods/breakfast_eggs.jpg`
  - `assets/foods/lunch_chicken.jpg`
  - `assets/foods/dinner_fish.jpg`

---

## ۴. روش ساخت فایل اجرایی یکپارچه (Windows .EXE)
برای اینکه برنامه بدون نیاز به نصب پایتون روی هر سیستم ویندوزی اجرا شود:

1. پکیج PyInstaller را نصب کنید:
```bash
pip install pyinstaller
```

2. دستور بیلد را اجرا نمایید:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "program_365.json;." main.py
```

3. فایل نهایی در پوشه `dist/main/main.exe` در دسترس خواهد بود.

---

## ۵. ساختار دایرکتوری‌های پروژه
```text
HeightProgram/
│
├── main.py                     # فایل اصلی اجرای برنامه در پایتون
├── program_365.json            # بانک اطلاعاتی جامع ۳۶۵ روزه
├── requirements.txt            # پکیج‌های پایتون
├── README.md                   # راهنمای کامل
│
├── assets/
│   ├── exercises/              # تصاویر و گیف‌های تمرینات
│   ├── foods/                  # تصاویر غذاها
│   ├── sounds/                 # صداهای بیپ تایمر و زنگ استراحت
│   └── icons/                  # آیکون‌ها
│
├── data/
│   └── settings.json           # تنظیمات کاربری
│
└── database/
    └── progress.db             # پایگاه داده SQLite سوابق
```
