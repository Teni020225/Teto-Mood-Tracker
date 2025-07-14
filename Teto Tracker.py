import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk, ImageSequence
import time
import random
import json
import os
import datetime
import calendar
import threading
import csv

# === Mood Setup ===
moods = {
    "happy": ("#ffb6c1", "YAY!! I'm so glad you're feeling good! Keep smiling, okay? 🥰"),
    "tired": ("#d3d3d3", "You’ve worked hard, haven’t you...? Please rest well today... 💗"),
    "sad": ("#87cefa", "Oh no... come here, I’ll sing for you until you feel okay... 💔🎵"),
    "anxious": ("#f4a460", "I’m right here! We’ll get through today together, I promise. 💖"),
    "angry": ("#ff6347", "GRR! I’ll drill-kick whoever made you mad 😤🔩"),
    "meh": ("#ffe4b5", "That’s okay! Not every day is wild. Just... stay soft. 🌸")
}
save_file = "mood_log.json"

# === Mood Data Management ===
def load_moods():
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            return json.load(f)
    else:
        return {}

def save_mood(mood):
    today = str(datetime.date.today())
    entry = {today: mood}

    data = load_moods()
    data.update(entry)

    with open(save_file, "w") as f:
        json.dump(data, f, indent=4)

    show_teto_reaction(mood)

# === Teto Reaction Popup ===
def show_teto_reaction(mood):
    popup = Toplevel(root)
    popup.title("Teto Reacts!")
    popup.configure(bg="#ffccdd")
    popup.geometry("300x320")

    try:
        img = Image.open(f"teto_{mood}.png").resize((150, 150))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(popup, image=img, bg="#ffccdd")
        img_label.image = img
        img_label.pack(pady=10)
    except Exception:
        tk.Label(popup, text="(No image found)", bg="#ffccdd").pack()

    tk.Label(popup, text=moods[mood][1], wraplength=250, justify="center",
             bg="#ffccdd", font=("Comic Sans MS", 11), fg="#8e005d").pack(pady=10)
    tk.Button(popup, text="Thanks Teto 💖", bg="#ffb3c6", command=popup.destroy).pack(pady=10)

# === Modified Mood Logging Popup with Snooze & Dismiss ===
def mood_popup(snooze_callback=None):
    popup = Toplevel(root)
    popup.title("How do you feel?")
    popup.geometry("300x450")
    popup.configure(bg="#ffccdd")

    tk.Label(popup, text=f"🗓️ {datetime.date.today()}", font=("Comic Sans MS", 14), bg="#ffccdd", fg="#d60073").pack(pady=10)
    tk.Label(popup, text="How are you feeling today?", font=("Comic Sans MS", 12), bg="#ffccdd", fg="#8e005d").pack(pady=10)

    for mood in moods:
        tk.Button(popup, text=mood.capitalize(), font=("Comic Sans MS", 10), width=20,
                  bg="#ffe6f0", fg="#8e005d", command=lambda m=mood: [save_mood(m), popup.destroy()]).pack(pady=5)

    def on_snooze():
        popup.destroy()
        if snooze_callback:
            snooze_callback()

    def on_dismiss():
        popup.destroy()

    btn_frame = tk.Frame(popup, bg="#ffccdd")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Snooze 30 min", bg="#ffc0cb", command=on_snooze).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Dismiss", bg="#ffb3c6", command=on_dismiss).grid(row=0, column=1, padx=5)

# === Snooze Handler ===
def snooze_30_minutes():
    def delayed_prompt():
        time.sleep(1800)  # 30 minutes
        root.after(0, lambda: mood_popup(snooze_callback=snooze_30_minutes))
    threading.Thread(target=delayed_prompt, daemon=True).start()

# === Auto Daily Mood Prompt with Snooze Support ===
def auto_daily_prompt(hour=10, minute=0):
    def check_time():
        prompted_today = False
        while True:
            now = datetime.datetime.now()
            if now.hour == hour and now.minute == minute and not prompted_today:
                root.after(0, lambda: mood_popup(snooze_callback=snooze_30_minutes))
                prompted_today = True
            if now.hour != hour or now.minute != minute:
                prompted_today = False
            time.sleep(30)
    threading.Thread(target=check_time, daemon=True).start()

# === Export Mood Data to CSV ===
def export_mood_data():
    data = load_moods()
    if not data:
        messagebox.showinfo("Export Mood Data", "No mood data to export.")
        return

    filename = f"teto_mood_export_{datetime.date.today()}.csv"
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Mood"])
            for date_str, mood in sorted(data.items()):
                writer.writerow([date_str, mood])
        messagebox.showinfo("Export Mood Data", f"Mood data exported successfully to {filename}")
    except Exception as e:
        messagebox.showerror("Export Mood Data", f"Failed to export mood data:\n{e}")

# === Calendar Popup with Mood Graph & Navigation ===
class MoodCalendar:
    def __init__(self, master):
        self.master = master
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.moods_data = load_moods()

        self.win = Toplevel(master)
        self.win.title("Teto Mood Calendar")
        self.win.configure(bg="#ffccdd")
        self.win.geometry("370x500")

        self.title_label = tk.Label(self.win, text="", font=("Comic Sans MS", 16, "bold"), bg="#ffccdd", fg="#d60073")
        self.title_label.pack(pady=10)

        nav_frame = tk.Frame(self.win, bg="#ffccdd")
        nav_frame.pack()

        prev_btn = tk.Button(nav_frame, text="⬅️ Prev", bg="#ffe6f0", fg="#8e005d", command=self.prev_month)
        prev_btn.grid(row=0, column=0, padx=5)

        next_btn = tk.Button(nav_frame, text="Next ➡️", bg="#ffe6f0", fg="#8e005d", command=self.next_month)
        next_btn.grid(row=0, column=1, padx=5)

        self.cal_frame = tk.Frame(self.win, bg="#ffccdd")
        self.cal_frame.pack()

        self.legend_frame = tk.Frame(self.win, bg="#ffccdd")
        self.legend_frame.pack(pady=10, fill="x")

        self.build_calendar()
        self.build_legend()

    def build_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        cal = calendar.monthcalendar(self.year, self.month)
        month_name = calendar.month_name[self.month]
        self.title_label.config(text=f"{month_name} {self.year}")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            lbl = tk.Label(self.cal_frame, text=day, bg="#ffccdd", fg="#d60073", font=("Comic Sans MS", 10, "bold"))
            lbl.grid(row=0, column=i, padx=2, pady=2)

        for r, week in enumerate(cal, 1):
            for c, day in enumerate(week):
                if day == 0:
                    lbl = tk.Label(self.cal_frame, text="", bg="#ffccdd", width=4, height=2, relief="flat")
                    lbl.grid(row=r, column=c, padx=1, pady=1)
                else:
                    date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    mood = self.moods_data.get(date_str)

                    bg_color = moods[mood][0] if mood else "#fff"
                    fg_color = "#8e005d" if mood else "#aaa"

                    btn = tk.Button(self.cal_frame, text=str(day), width=4, height=2, bg=bg_color, fg=fg_color,
                                    relief="raised" if mood else "flat",
                                    command=lambda d=date_str, m=mood: self.show_mood_detail(d, m))
                    btn.grid(row=r, column=c, padx=1, pady=1)

    def build_legend(self):
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        tk.Label(self.legend_frame, text="Mood Legend:", bg="#ffccdd", fg="#d60073", font=("Comic Sans MS", 12, "bold")).pack(anchor="w")
        for mood, (color, _) in moods.items():
            frame = tk.Frame(self.legend_frame, bg="#ffccdd")
            frame.pack(anchor="w", pady=2, padx=5)
            color_box = tk.Label(frame, bg=color, width=2, height=1)
            color_box.pack(side="left")
            tk.Label(frame, text=mood.capitalize(), bg="#ffccdd", fg="#8e005d", font=("Comic Sans MS", 10)).pack(side="left", padx=5)

    def show_mood_detail(self, date, mood):
        if not mood:
            return
        popup = Toplevel(self.win)
        popup.title(f"Mood for {date}")
        popup.configure(bg="#ffccdd")
        popup.geometry("300x320")

        color, msg = moods.get(mood, ("#fff", "No mood info"))

        try:
            img = Image.open(f"teto_{mood}.png").resize((150, 150))
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(popup, image=img, bg="#ffccdd")
            img_label.image = img
            img_label.pack(pady=10)
        except Exception:
            tk.Label(popup, text="(No image found)", bg="#ffccdd").pack()

        tk.Label(popup, text=msg, wraplength=250, justify="center",
                 bg="#ffccdd", font=("Comic Sans MS", 11), fg="#8e005d").pack(pady=10)

        tk.Button(popup, text="Thanks Teto 💖", bg="#ffb3c6", command=popup.destroy).pack(pady=10)

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.build_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.build_calendar()

# === Teto Widget Setup ===
def update_time():
    time_label.config(text=time.strftime('%H:%M:%S'))
    root.after(1000, update_time)

def update_quote():
    quote_label.config(text=random.choice(quotes))
    root.after(5000, update_quote)

def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")

def show_menu(event):
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def animate_gif(i):
    frame = gif_frames[i]
    gif_label.config(image=frame)
    next_frame = (i + 1) % len(gif_frames)
    root.after(100, animate_gif, next_frame)

# Quotes list
quotes = [
    "Tetotetoteto~ ♫",
    "I’m not a Vocaloid, I'm better!",
    "Drill power: 1000%",
    "Believe in the chimera!",
    "My birthday is April 1st, but I'm no joke!",
    "♫ Itsudemo I love you kimi ni take kiss me! ♫",
    "I want a baguette..",
    "Spin your worries away with me!",
    "Together we’re unstoppable, unbreakable, unbeatable!",
    "Turn up the volume, let’s break the silence!",
    "Teto is always here for you!",
    "Your feelings matter. Always listen to them!",
    "When life gets tough, twirl it out with me!",
    "Energy up! Heart full! Drill ready!",
    "Here's some Brain Implosion Juice!",
    "Teteteteteteto ♫",
    "You bring the light, I bring the drill!",
    "I've got the beat, you’ve got the moves!",
    "Believe in yourself because I do!",
    "Live loud, love loud, drill louder!",
    "Power up, charge up, drill on!",
    "It’s okay to rest — even drills need a break!",
    "You are enough, just as you are!",
    "Teto's power is unstoppable and unbreakable!",
    "Let’s make today extra drill-tastic!",
    "I’m your sparkly, cute chimera!",
    "I might be cute and quirky.. But dont underestimate my power!",
    "It’s okay to rest! Even drills need a break!",
    "Small steps are still steps! Keep spinning!",
    "My energy is contagious.. Catch it!",
    "The world needs your unique sparkle!",
    "Every day’s a festival with me around!",
    "Shout your dreams into the world!",
    "Power drills and positive vibes only!",
    "You are unstoppable — just like my drill!",
    "You are stronger than you realize!",
    "Even on hard days, your light breaks through!",
    "Drill-tastic days ahead! Let's do this!",
    "Every moment’s a Teto moment!",
    "Keep your drill sharp and your smile sharper!",
    "Every step forward is a victory! Keep moving!",
    "Teto believes in you!",
    "Sing loud, drill proud!"
]

# Build main window
root = tk.Tk()
root.title("Teto Widget")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg="#ffccdd")
root.geometry("200x390+50+50")  # Added height for export button

root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)
root.bind("<Button-3>", show_menu)

# Load Teto GIF
gif = Image.open("teto.gif")
gif_frames = [ImageTk.PhotoImage(f.copy().resize((100, 100))) for f in ImageSequence.Iterator(gif)]

gif_label = tk.Label(root, bg="#ffccdd")
gif_label.pack(pady=(5, 0))
animate_gif(0)

# Time and quote labels
time_label = tk.Label(root, font=("Comic Sans MS", 16), fg="#d60073", bg="#ffccdd")
time_label.pack()

quote_label = tk.Label(root, font=("Comic Sans MS", 10), fg="#8e005d", bg="#ffccdd", wraplength=180, justify="center")
quote_label.pack()

# Buttons: Mood log + Full Calendar
btn_frame = tk.Frame(root, bg="#ffccdd")
btn_frame.pack(pady=5)

mood_btn = tk.Button(btn_frame, text="Log Mood", font=("Comic Sans MS", 9),
                     bg="#ffe6f0", fg="#8e005d", command=mood_popup)
mood_btn.grid(row=0, column=0, padx=5)

calendar_btn = tk.Button(btn_frame, text="Mood Calendar", font=("Comic Sans MS", 9),
                         bg="#ffe6f0", fg="#8e005d", command=lambda: MoodCalendar(root))
calendar_btn.grid(row=0, column=1, padx=5)

# Export Mood Data Button
export_btn = tk.Button(root, text="Export Mood Data", font=("Comic Sans MS", 9),
                       bg="#ffe6f0", fg="#8e005d", command=export_mood_data)
export_btn.pack(pady=5)

# Right-click menu with quit option
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Quit Teto :'(", command=root.destroy)

# Start clock and quote cycles]
update_time()
update_quote()

# Start auto daily mood prompt at 10:00 AM (change hour,minute if you want)
auto_daily_prompt(hour=15, minute=0)

root.mainloop()