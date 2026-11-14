import queue
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox

import numpy as np
import pyaudio
import win32api
import win32con
import win32gui

WINDOW_TITLE = "World of Warcraft"
DEFAULT_THRESHOLD = -45
CHUNK = 1024
RATE = 44100
CAST_TIMEOUT = 30
LISTEN_DELAY = 2
MIN_RMS = 1e-10
DB_FLOOR = -80
DB_CEIL = 0

BG = "#0e1a20"
PANEL = "#15262e"
TEXT = "#e8eff2"
MUTED = "#86a0aa"
WATER = "#3fb6c4"
GOLD = "#f0b94a"
RED = "#e5604d"
GREEN = "#6cc58a"

FONT = "Segoe UI"
MONO = "Consolas"


def find_stereo_mix(p):
    for i in range(p.get_device_count()):
        if "Stereo Mix" in p.get_device_info_by_index(i)["name"]:
            return i
    return None


class Worker(threading.Thread):
    def __init__(self, events, shared, hwnd, device_index, initial_cast):
        super().__init__(daemon=True)
        self.events = events
        self.shared = shared
        self.hwnd = hwnd
        self.device_index = device_index
        self.initial_cast = initial_cast
        self.stop = threading.Event()

    def emit(self, *event):
        self.events.put(event)

    def make_cast(self):
        scan = win32api.MapVirtualKey(win32con.VK_F6, 0)
        down = 1 | (scan << 16)
        up = 1 | (scan << 16) | (1 << 30) | (1 << 31)

        def cast(is_bait):
            win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_F6, down)
            win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_F6, up)
            self.emit("bait" if is_bait else "catch")

        return cast

    def run(self):
        p = pyaudio.PyAudio()
        stream = None
        try:
            cast = self.make_cast()
            if self.initial_cast:
                cast(True)
                self.emit("settle")
                self.stop.wait(LISTEN_DELAY)
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                            input_device_index=self.device_index,
                            frames_per_buffer=CHUNK, start=False)

            while not self.stop.is_set():
                started = time.time()
                self.emit("listen", started)
                stream.start_stream()

                while not self.stop.is_set():
                    try:
                        raw = stream.read(CHUNK, exception_on_overflow=False)
                    except Exception as e:
                        self.emit("error", str(e))
                        break

                    samples = np.frombuffer(raw, dtype=np.int16) / 32768.0
                    rms = max(np.sqrt(np.mean(samples ** 2)), MIN_RMS)
                    db = round(20 * np.log10(rms))
                    self.emit("db", db)

                    if db > self.shared["threshold"]:
                        self.emit("splash", db)
                        if self.stop.wait(random.uniform(0.5, 1)):
                            break
                        cast(False)
                        break
                    if time.time() - started > CAST_TIMEOUT:
                        self.emit("timeout")
                        break

                stream.stop_stream()
                if self.stop.is_set():
                    break
                self.emit("wait")
                if self.stop.wait(random.uniform(3, 5)):
                    break
                cast(True)
                self.emit("settle")
                if self.stop.wait(LISTEN_DELAY):
                    break
        except Exception as e:
            self.emit("error", str(e))
        finally:
            if stream is not None:
                stream.close()
            p.terminate()
            self.emit("stopped")


class App:
    def __init__(self, root):
        self.root = root
        root.title("Fishing Assistant")
        root.configure(bg=BG)

        self.events = queue.Queue()
        self.shared = {"threshold": DEFAULT_THRESHOLD}
        self.worker = None
        self.first_start = True
        self.db = DB_FLOOR
        self.run_started = None
        self.elapsed_before = 0.0
        self.cast_started = None
        self.counts = {"casts": 0}

        self.build()
        root.update_idletasks()
        width = max(560, root.winfo_reqwidth())
        height = max(720, root.winfo_reqheight())
        root.geometry(f"{width}x{height}")
        root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
        self.set_status("Ready", MUTED)
        self.log("Press Start, then switch to the game.", MUTED)
        root.bind("<space>", lambda e: self.toggle())
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll()
        self.tick()

    def build(self):
        pad = 20
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill="x", padx=pad, pady=(pad, 8))
        tk.Label(head, text="Fishing Assistant", bg=BG, fg=TEXT,
                 font=(FONT, 18, "bold")).pack(side="left")
        pill = tk.Frame(head, bg=PANEL, padx=12, pady=5)
        pill.pack(side="right")
        self.dot = tk.Canvas(pill, width=10, height=10, bg=PANEL, highlightthickness=0)
        self.dot.pack(side="left", padx=(0, 8))
        self.dot_id = self.dot.create_oval(1, 1, 9, 9, fill=MUTED, outline="")
        self.status = tk.Label(pill, text="", bg=PANEL, fg=TEXT, font=(FONT, 10))
        self.status.pack(side="left")

        sound = tk.Frame(self.root, bg=PANEL)
        sound.pack(fill="x", padx=pad, pady=8)
        top = tk.Frame(sound, bg=PANEL)
        top.pack(fill="x", padx=16, pady=(14, 0))
        self.db_label = tk.Label(top, text="--", bg=PANEL, fg=TEXT, font=(FONT, 44, "bold"))
        self.db_label.pack(side="left")
        tk.Label(top, text="dB", bg=PANEL, fg=MUTED, font=(FONT, 14)).pack(
            side="left", anchor="s", padx=(6, 0), pady=(0, 12))
        self.hint = tk.Label(top, text="Waiting to start", bg=PANEL, fg=MUTED,
                             font=(FONT, 10), justify="right")
        self.hint.pack(side="right", anchor="s", pady=(0, 12))

        self.meter = tk.Canvas(sound, height=26, bg=PANEL, highlightthickness=0)
        self.meter.pack(fill="x", padx=16, pady=(6, 4))
        self.meter.bind("<Configure>", lambda e: self.draw_meter())

        row = tk.Frame(sound, bg=PANEL)
        row.pack(fill="x", padx=16, pady=(4, 14))
        tk.Label(row, text="Splash threshold", bg=PANEL, fg=MUTED, font=(FONT, 10)).pack(side="left")
        self.thr_label = tk.Label(row, text=f"{DEFAULT_THRESHOLD} dB", bg=PANEL, fg=TEXT,
                                  font=(FONT, 10, "bold"))
        self.thr_label.pack(side="right")
        self.slider = tk.Scale(sound, from_=DB_FLOOR, to=DB_CEIL, orient="horizontal",
                               showvalue=False, bg=PANEL, fg=TEXT, troughcolor=BG,
                               highlightthickness=0, bd=0, sliderrelief="flat",
                               activebackground=WATER, command=self.on_threshold)
        self.slider.set(DEFAULT_THRESHOLD)
        self.slider.pack(fill="x", padx=16, pady=(0, 14))

        stats = tk.Frame(self.root, bg=BG)
        stats.pack(fill="x", padx=pad, pady=8)
        for i in range(3):
            stats.columnconfigure(i, weight=1, uniform="s")
        self.session_val = self.stat(stats, 0, "Session time", "00:00:00")
        self.cast_val = self.stat(stats, 1, "Time left on this cast", "--")
        self.count_val = self.stat(stats, 2, "Casts", "0")

        self.cast_bar = tk.Canvas(self.root, height=4, bg=PANEL, highlightthickness=0)
        self.cast_bar.pack(fill="x", padx=pad, pady=(0, 8))

        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack(side="bottom", fill="x", padx=pad, pady=pad)
        buttons.columnconfigure(0, weight=1, uniform="b")
        buttons.columnconfigure(1, weight=1, uniform="b")
        self.start_btn = self.button(buttons, "Start", WATER, BG, self.start)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_btn = self.button(buttons, "Stop", PANEL, TEXT, self.stop)
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.set_buttons(running=False)

        tk.Label(self.root, text="Activity", bg=BG, fg=MUTED, font=(FONT, 10),
                 anchor="w").pack(fill="x", padx=pad, pady=(8, 4))
        logwrap = tk.Frame(self.root, bg=PANEL)
        logwrap.pack(fill="both", expand=True, padx=pad)
        self.logbox = tk.Text(logwrap, height=6, bg=PANEL, fg=TEXT, font=(MONO, 10), bd=0,
                              highlightthickness=0, wrap="word", state="disabled",
                              padx=12, pady=10, cursor="arrow")
        scroll = tk.Scrollbar(logwrap, command=self.logbox.yview)
        self.logbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.logbox.pack(side="left", fill="both", expand=True)
        for name, color in (("muted", MUTED), ("water", WATER), ("gold", GOLD),
                            ("red", RED), ("green", GREEN), ("text", TEXT)):
            self.logbox.tag_configure(name, foreground=color)


    def stat(self, parent, col, name, value):
        box = tk.Frame(parent, bg=PANEL)
        box.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0 if col == 2 else 6))
        tk.Label(box, text=name, bg=PANEL, fg=MUTED, font=(FONT, 9), anchor="w").pack(
            fill="x", padx=12, pady=(10, 0))
        val = tk.Label(box, text=value, bg=PANEL, fg=TEXT, font=(FONT, 15, "bold"), anchor="w")
        val.pack(fill="x", padx=12, pady=(0, 10))
        return val

    def button(self, parent, text, bg, fg, command):
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, bd=0,
                      font=(FONT, 12, "bold"), pady=10, cursor="hand2", takefocus=0,
                      activebackground=bg, activeforeground=fg, relief="flat",
                      disabledforeground=MUTED)
        b.base = bg
        return b

    def set_buttons(self, running):
        self.start_btn.configure(state="disabled" if running else "normal",
                                 bg=PANEL if running else WATER,
                                 cursor="arrow" if running else "hand2")
        self.stop_btn.configure(state="normal" if running else "disabled",
                                bg=RED if running else PANEL,
                                fg=BG if running else MUTED,
                                cursor="hand2" if running else "arrow")

    def set_status(self, text, color):
        self.status.configure(text=text)
        self.dot.itemconfigure(self.dot_id, fill=color)

    def log(self, message, tag="text"):
        stamp = time.strftime("%H:%M:%S")
        self.logbox.configure(state="normal")
        self.logbox.insert("end", f"{stamp}  ", "muted")
        self.logbox.insert("end", message + "\n", tag)
        lines = int(self.logbox.index("end-1c").split(".")[0])
        if lines > 300:
            self.logbox.delete("1.0", f"{lines - 300}.0")
        self.logbox.configure(state="disabled")
        self.logbox.see("end")

    def on_threshold(self, value):
        value = int(float(value))
        self.shared["threshold"] = value
        self.thr_label.configure(text=f"{value} dB")
        self.draw_meter()

    def draw_meter(self):
        c = self.meter
        c.delete("all")
        w = max(c.winfo_width(), 1)
        h = 26
        span = DB_CEIL - DB_FLOOR
        c.create_rectangle(0, 6, w, h - 6, fill=BG, outline="")
        level = min(max((self.db - DB_FLOOR) / span, 0), 1)
        hot = self.db > self.shared["threshold"]
        c.create_rectangle(0, 6, w * level, h - 6, fill=GOLD if hot else WATER, outline="")
        x = w * (self.shared["threshold"] - DB_FLOOR) / span
        c.create_line(x, 1, x, h - 1, fill=TEXT, width=2)

    def draw_cast_bar(self, fraction):
        c = self.cast_bar
        c.delete("all")
        w = max(c.winfo_width(), 1)
        if fraction is not None:
            c.create_rectangle(0, 0, w * fraction, 4, fill=WATER, outline="")

    def toggle(self):
        if self.worker is None:
            self.start()
        else:
            self.stop()

    def start(self):
        if self.worker is not None:
            return
        hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
        if not hwnd:
            self.log(f"Couldn't find the '{WINDOW_TITLE}' window. Open the game and try again.", "red")
            messagebox.showerror("Game not found",
                                 f"Couldn't find a window titled '{WINDOW_TITLE}'.\nOpen the game and try again.")
            return
        p = pyaudio.PyAudio()
        device = find_stereo_mix(p)
        p.terminate()
        if device is None:
            self.log("No 'Stereo Mix' input device found.", "red")
            messagebox.showerror("Audio device not found",
                                 "No 'Stereo Mix' input device found.\n"
                                 "Enable it in Windows Sound settings > Recording, then try again.")
            return
        self.worker = Worker(self.events, self.shared, hwnd, device, self.first_start)
        self.first_start = False
        self.run_started = time.time()
        self.worker.start()
        self.set_buttons(running=True)
        self.log("Started", "green")

    def stop(self):
        if self.worker is None:
            return
        self.worker.stop.set()
        self.stop_btn.configure(state="disabled")
        self.set_status("Stopping", MUTED)

    def update_counts(self):
        self.count_val.configure(text=str(self.counts["casts"]))

    def handle(self, event):
        kind = event[0]
        if kind == "db":
            self.db = event[1]
        elif kind == "listen":
            self.cast_started = event[1]
            self.set_status("Listening for a splash", WATER)
            self.hint.configure(text="Watching the audio level")
        elif kind == "splash":
            self.set_status("Splash detected", GOLD)
            self.hint.configure(text=f"Peaked at {event[1]} dB")
            self.log(f"Splash detected at {event[1]} dB", "gold")
        elif kind == "catch":
            self.log("You caught something", "green")
        elif kind == "bait":
            self.counts["casts"] += 1
            self.update_counts()
            self.log("You threw the lure", "water")
        elif kind == "timeout":
            self.log(f"No splash in {CAST_TIMEOUT}s, recasting", "muted")
        elif kind == "settle":
            self.cast_started = None
            self.set_status("Lure in the water", GOLD)
            self.hint.configure(text=f"Listening starts in {LISTEN_DELAY}s")
        elif kind == "wait":
            self.cast_started = None
            self.set_status("Recasting soon", GOLD)
            self.hint.configure(text="Pausing before the next cast")
        elif kind == "error":
            self.log(f"Error: {event[1]}", "red")
        elif kind == "stopped":
            if self.run_started is not None:
                self.elapsed_before += time.time() - self.run_started
            self.run_started = None
            self.cast_started = None
            self.worker = None
            self.db = DB_FLOOR
            self.db_label.configure(text="--", fg=TEXT)
            self.hint.configure(text="Stopped. Press Start to resume.")
            self.set_status("Stopped", MUTED)
            self.set_buttons(running=False)
            self.log("Stopped", "muted")
            self.draw_meter()

    def poll(self):
        latest_db = None
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "db":
                    self.db = event[1]
                    latest_db = event[1]
                else:
                    self.handle(event)
        except queue.Empty:
            pass
        if latest_db is not None and self.worker is not None:
            hot = latest_db > self.shared["threshold"]
            self.db_label.configure(text=str(latest_db), fg=GOLD if hot else TEXT)
            self.draw_meter()
        self.root.after(40, self.poll)

    def tick(self):
        total = self.elapsed_before
        if self.run_started is not None:
            total += time.time() - self.run_started
        h, rem = divmod(int(total), 3600)
        m, s = divmod(rem, 60)
        self.session_val.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
        if self.cast_started is not None:
            left = max(0.0, CAST_TIMEOUT - (time.time() - self.cast_started))
            self.cast_val.configure(text=f"{left:0.1f}s")
            self.draw_cast_bar(left / CAST_TIMEOUT)
        else:
            self.cast_val.configure(text="--")
            self.draw_cast_bar(None)
        self.root.after(100, self.tick)

    def close(self):
        if self.worker is not None:
            self.worker.stop.set()
            self.worker.join(timeout=2)
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()