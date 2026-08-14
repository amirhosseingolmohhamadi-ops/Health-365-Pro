# -*- coding: utf-8 -*-
"""
برنامه سلامت و رشد ۳۶۵ روزه - نسخه دسکتاپ حرفه‌ای Python (CustomTkinter / Tkinter)
ویژه نوجوان ۱۵ ساله (قد: ۱۷۲ سانتیمتر | وزن: ۴۵ کیلوگرم)
تجهیزات: تردمیل، بارفیکس، توپ بزرگ ورزشی، کش ورزشی، دستگاه مسگری
"""

import os
import sys
import json
import sqlite3
import datetime
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# تلاش برای بارگذاری CustomTkinter با فال‌بک امن به Tkinter استاندارد
USE_CUSTOMTKINTER = True
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")
except ImportError:
    USE_CUSTOMTKINTER = False

# مسیرهای پایگاه داده و فایل‌ها
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "progress.db")
PROGRAM_JSON_PATH = os.path.join(BASE_DIR, "program_365.json")

# پایگاه داده SQLite
def init_db():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            day_number INTEGER PRIMARY KEY,
            completed_exercises TEXT,
            eaten_meals TEXT,
            sleep_hours REAL,
            sleep_rating INTEGER,
            is_day_completed INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY,
            current_day INTEGER DEFAULT 1,
            height_cm REAL DEFAULT 172.0,
            weight_kg REAL DEFAULT 45.0,
            sound_enabled INTEGER DEFAULT 1
        )
    ''')
    cur.execute('INSERT OR IGNORE INTO user_settings (id, current_day, height_cm, weight_kg, sound_enabled) VALUES (1, 1, 172.0, 45.0, 1)')
    conn.commit()
    conn.close()

def load_program_json():
    if os.path.exists(PROGRAM_JSON_PATH):
        try:
            with open(PROGRAM_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {PROGRAM_JSON_PATH}: {e}")
    # اگر فایل پیدا نشد یک ساختار پیش‌فرض ایجاد کن
    return []

class DesktopHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامه سلامت و رشد ۳۶۵ روزه - نسخه دسکتاپ")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)

        init_db()
        self.program_data = load_program_json()
        self.current_day = self.get_saved_current_day()
        self.current_exercise_idx = 0

        # وضعیت تایمر تمرین
        self.timer_seconds_left = 60
        self.is_timer_running = False
        self.timer_thread = None

        # وضعیت تایمر استراحت
        self.rest_seconds_left = 30
        self.is_resting = False

        # شمارنده تکرار
        self.current_set = 1
        self.current_reps = 0

        self.setup_ui()
        self.refresh_day_data()

    def get_saved_current_day(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('SELECT current_day FROM user_settings WHERE id = 1')
            row = cur.fetchone()
            conn.close()
            if row:
                return row[0]
        except Exception:
            pass
        return 1

    def save_current_day(self, day):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('UPDATE user_settings SET current_day = ? WHERE id = 1', (day,))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def setup_ui(self):
        if USE_CUSTOMTKINTER:
            self.header = ctk.CTkFrame(self.root, height=55, corner_radius=0)
            self.header.pack(fill="x", side="top", padx=0, pady=0)

            self.title_label = ctk.CTkLabel(
                self.header,
                text="برنامه جامع سلامت و رشد ۳۶۵ روزه",
                font=ctk.CTkFont(family="Tahoma", size=15, weight="bold")
            )
            self.title_label.pack(side="right", padx=20, pady=12)

            self.day_label = ctk.CTkLabel(
                self.header,
                text=f"DAY {self.current_day} / 365",
                font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                text_color="#10b981"
            )
            self.day_label.pack(side="left", padx=20, pady=12)

            # دکمه‌های روز قبل / روز بعد
            self.btn_next_day = ctk.CTkButton(self.header, text="روز بعد >", width=75, command=self.next_day)
            self.btn_next_day.pack(side="left", padx=5)

            self.btn_prev_day = ctk.CTkButton(self.header, text="< روز قبل", width=75, command=self.prev_day)
            self.btn_prev_day.pack(side="left", padx=5)

            # تب‌ها
            self.tabview = ctk.CTkTabview(self.root, corner_radius=12)
            self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

            self.tab_dash = self.tabview.add("داشبورد (Dashboard)")
            self.tab_workout = self.tabview.add("ورزش (Workout)")
            self.tab_nutrition = self.tabview.add("تغذیه (Nutrition)")
            self.tab_sleep = self.tabview.add("خواب (Sleep)")
            self.tab_progress = self.tabview.add("پیشرفت (Progress)")

            self.build_dashboard_ui()
            self.build_workout_ui()
            self.build_nutrition_ui()
            self.build_sleep_ui()
            self.build_progress_ui()
        else:
            # Fallback Tkinter UI
            lbl = tk.Label(self.root, text=f"DAY {self.current_day} / 365", font=("Arial", 16, "bold"))
            lbl.pack(pady=20)

    def build_dashboard_ui(self):
        self.dash_title = ctk.CTkLabel(self.tab_dash, text="", font=ctk.CTkFont(family="Tahoma", size=18, weight="bold"))
        self.dash_title.pack(pady=10)

        self.dash_focus = ctk.CTkLabel(self.tab_dash, text="", text_color="gray", font=ctk.CTkFont(family="Tahoma", size=13))
        self.dash_focus.pack(pady=5)

        # کارت‌های وضعیت
        self.cards_frame = ctk.CTkFrame(self.tab_dash)
        self.cards_frame.pack(fill="x", padx=20, pady=20)

        self.w_card = ctk.CTkLabel(self.cards_frame, text="ورزش: آماده شروع", font=ctk.CTkFont(family="Tahoma", size=13))
        self.w_card.grid(row=0, column=0, padx=20, pady=20)

        self.n_card = ctk.CTkLabel(self.cards_frame, text="تغذیه: ۶ وعده کامل", font=ctk.CTkFont(family="Tahoma", size=13))
        self.n_card.grid(row=0, column=1, padx=20, pady=20)

        self.s_card = ctk.CTkLabel(self.cards_frame, text="خواب: ۲۳:۰۰ تا ۰۷:۳۰ (۸.۵ ساعت)", font=ctk.CTkFont(family="Tahoma", size=13))
        self.s_card.grid(row=0, column=2, padx=20, pady=20)

        # هشدار ایمنی
        self.safety_box = ctk.CTkLabel(
            self.tab_dash,
            text="هشدار: این برنامه افزایش قد را تضمین نمیکند. هدف آن سلامت، آمادگی جسمانی، خواب و تغذیه است.\nدرد تیز = توقف تمرین | عدم مصرف خودسرانه هورمون رشد",
            text_color="#f59e0b",
            font=ctk.CTkFont(family="Tahoma", size=11)
        )
        self.safety_box.pack(pady=15)

    def build_workout_ui(self):
        self.ex_name_lbl = ctk.CTkLabel(self.tab_workout, text="حرکت ورزشی", font=ctk.CTkFont(family="Tahoma", size=16, weight="bold"))
        self.ex_name_lbl.pack(pady=10)

        # تایمر دیجیتال
        self.timer_lbl = ctk.CTkLabel(self.tab_workout, text="01:00", font=ctk.CTkFont(family="Consolas", size=48, weight="bold"), text_color="#10b981")
        self.timer_lbl.pack(pady=15)

        # دکمه‌های تایمر
        self.t_btns_frame = ctk.CTkFrame(self.tab_workout)
        self.t_btns_frame.pack(pady=10)

        self.btn_start = ctk.CTkButton(self.t_btns_frame, text="شروع (START)", command=self.start_timer, fg_color="#10b981")
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_pause = ctk.CTkButton(self.t_btns_frame, text="توقف (PAUSE)", command=self.pause_timer, fg_color="#f59e0b")
        self.btn_pause.grid(row=0, column=1, padx=5)

        self.btn_reset = ctk.CTkButton(self.t_btns_frame, text="بازنشانی (RESET)", command=self.reset_timer, fg_color="#64748b")
        self.btn_reset.grid(row=0, column=2, padx=5)

        # بخش تکرارها
        self.rep_frame = ctk.CTkFrame(self.tab_workout)
        self.rep_frame.pack(pady=15)

        self.rep_lbl = ctk.CTkLabel(self.rep_frame, text="تکرارها: 0 / 10 | ست 1 از 3", font=ctk.CTkFont(family="Tahoma", size=14))
        self.rep_lbl.pack(padx=20, pady=10)

        self.btn_add_rep = ctk.CTkButton(self.rep_frame, text="+1 تکرار (+1 REP)", command=self.add_rep, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_add_rep.pack(padx=20, pady=10)

    def build_nutrition_ui(self):
        lbl = ctk.CTkLabel(self.tab_nutrition, text="برنامه ۶ وعده غذایی روزانه غنی از پروتئین و کلسیم", font=ctk.CTkFont(family="Tahoma", size=15, weight="bold"))
        lbl.pack(pady=10)

        self.meals_box = ctk.CTkTextbox(self.tab_nutrition, width=700, height=350, font=ctk.CTkFont(family="Tahoma", size=12))
        self.meals_box.pack(pady=10)

    def build_sleep_ui(self):
        lbl = ctk.CTkLabel(self.tab_sleep, text="برنامه خواب منظم شبانه (۲۳:۰۰ الی ۰۷:۳۰)", font=ctk.CTkFont(family="Tahoma", size=16, weight="bold"), text_color="#818cf8")
        lbl.pack(pady=15)

        desc = ctk.CTkLabel(
            self.tab_sleep,
            text="• ترشح هورمون رشد (GH) در فاز خواب عمیق شبانه رخ می‌دهد.\n• از ساعت ۲۲:۰۰ نمایشگرها را خاموش کنید.\n• دمای اتاق ۱۹ تا ۲۱ درجه و محیط کاملاً تاریک باشد.",
            font=ctk.CTkFont(family="Tahoma", size=13),
            justify="right"
        )
        desc.pack(pady=15)

    def build_progress_ui(self):
        lbl = ctk.CTkLabel(self.tab_progress, text="گزارش پیشرفت و ثبت قد و وزن", font=ctk.CTkFont(family="Tahoma", size=15, weight="bold"))
        lbl.pack(pady=15)

        self.stats_lbl = ctk.CTkLabel(self.tab_progress, text="قد: ۱۷۲ سانتیمتر | وزن: ۴۵ کیلوگرم | سن: ۱۵ سال", font=ctk.CTkFont(family="Tahoma", size=13))
        self.stats_lbl.pack(pady=10)

    def start_timer(self):
        if not self.is_timer_running:
            self.is_timer_running = True
            self.timer_thread = threading.Thread(target=self._run_timer_loop, daemon=True)
            self.timer_thread.start()

    def pause_timer(self):
        self.is_timer_running = False

    def reset_timer(self):
        self.is_timer_running = False
        self.timer_seconds_left = 60
        self.update_timer_display()

    def _run_timer_loop(self):
        while self.is_timer_running and self.timer_seconds_left > 0:
            time.sleep(1)
            self.timer_seconds_left -= 1
            self.update_timer_display()
            if self.timer_seconds_left <= 0:
                self.is_timer_running = False
                self.root.bell()
                messagebox.showinfo("پایان زمان", "زمان تمام شد، حرکت بعدی")

    def update_timer_display(self):
        mins = self.timer_seconds_left // 60
        secs = self.timer_seconds_left % 60
        self.timer_lbl.configure(text=f"{mins:02d}:{secs:02d}")

    def add_rep(self):
        self.current_reps += 1
        self.rep_lbl.configure(text=f"تکرارها: {self.current_reps} / 10 | ست {self.current_set} از 3")
        if self.current_reps >= 10:
            self.root.bell()
            messagebox.showinfo("ست کامل شد", f"ست {self.current_set} تکمیل شد! ۳۰ ثانیه استراحت کنید.")
            self.current_reps = 0
            if self.current_set < 3:
                self.current_set += 1

    def next_day(self):
        if self.current_day < 365:
            self.current_day += 1
            self.save_current_day(self.current_day)
            self.refresh_day_data()

    def prev_day(self):
        if self.current_day > 1:
            self.current_day -= 1
            self.save_current_day(self.current_day)
            self.refresh_day_data()

    def refresh_day_data(self):
        if USE_CUSTOMTKINTER:
            self.day_label.configure(text=f"DAY {self.current_day} / 365")
            self.dash_title.configure(text=f"برنامه روز {self.current_day}")
            self.dash_focus.configure(text=f"تمرکز: تقویت بالاتنه، بارفیکس، کش ورزشی و تغذیه کلسیم")
            
            # پر کردن وعده‌ها
            self.meals_box.delete("0.0", "end")
            self.meals_box.insert("0.0", f"وعده‌های غذایی روز {self.current_day}:\n\n۱. صبحانه: املت تخم مرغ + نان سنگک + شیر گرم با عسل\n۲. میان‌وعده صبح: ۱۰ عدد بادام + گردو + سیب\n۳. ناهار: فیله مرغ گریل شده + کته زعفرانی + ماست پرپروتئین\n۴. میان‌وعده عصر: اسموتی موز و کره بادام زمینی\n۵. بعد از تمرین: شیرکاکائو کم‌شیرین + خرما\n۶. شام: ماهی قزل‌آلا + سیب زمینی تنوری و کلم بروکلی")

if __name__ == "__main__":
    if USE_CUSTOMTKINTER:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    app = DesktopHealthApp(root)
    root.mainloop()
