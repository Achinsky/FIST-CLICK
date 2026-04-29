"""
FIST CLICK — Auto Clicker
Run: python fist_click.py
Build: pyinstaller fist_click.spec
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import threading
import time
import sys
import os

# runtime imports (Windows / X11)
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    PYAUTOGUI_OK = True
except Exception:
    PYAUTOGUI_OK = False

try:
    from pynput import mouse as pynmouse, keyboard as pynkeyboard
    PYNPUT_OK = True
except Exception:
    PYNPUT_OK = False

# THEME
C = {
    "bg":        "#0D0D0D",
    "panel":     "#141414",
    "card":      "#1A1A1A",
    "border":    "#2A2A2A",
    "accent":    "#FF3B30",
    "accent2":   "#FF6B35",
    "green":     "#30D158",
    "text":      "#FFFFFF",
    "text2":     "#8A8A8E",
    "text3":     "#48484A",
    "inactive":  "#2C2C2E",
    "hover":     "#222222",
}

MAX_SPOTS = 4


class ClickSpot:
    def __init__(self):
        self.x = None
        self.y = None
        self.enabled = True
        self.button = "left"   # "left" | "right"
        self.click_type = "single"  # "single" | "double"


class PickOverlay:
    """Fullscreen crosshair overlay. Click to capture X/Y."""
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.win = tk.Toplevel(root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.01)
        self.win.attributes("-topmost", True)
        self.win.config(cursor="crosshair", bg="#000000")

        self.canvas = tk.Canvas(self.win, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        info = tk.Label(
            self.win,
            text="\U0001f3af  Click anywhere to pick coordinates  \u2022  ESC to cancel",
            font=("Courier New", 13, "bold"),
            fg="#FFFFFF", bg="#1A1A1A",
            padx=20, pady=10,
        )
        info.place(relx=0.5, rely=0.5, anchor="center")

        self.win.bind("<Button-1>", self._on_click)
        self.win.bind("<Escape>", self._cancel)
        self.win.focus_force()

    def _on_click(self, event):
        x, y = event.x_root, event.y_root
        self.win.destroy()
        self.callback(x, y)

    def _cancel(self, event=None):
        self.win.destroy()
        self.callback(None, None)


class SpotCard(tk.Frame):
    def __init__(self, parent, index, spot: ClickSpot, app):
        super().__init__(parent, bg=C["card"], padx=12, pady=10,
                         highlightbackground=C["border"], highlightthickness=1)
        self.spot = spot
        self.index = index
        self.app = app

        hdr = tk.Frame(self, bg=C["card"])
        hdr.pack(fill="x", pady=(0, 8))

        self.num_lbl = tk.Label(
            hdr, text=f"SPOT {index+1}", font=("Courier New", 9, "bold"),
            fg=C["accent"], bg=C["card"]
        )
        self.num_lbl.pack(side="left")

        self.enable_var = tk.BooleanVar(value=spot.enabled)
        self.toggle_btn = tk.Checkbutton(
            hdr, variable=self.enable_var, text="ON",
            font=("Courier New", 8, "bold"),
            fg=C["green"], bg=C["card"], selectcolor=C["card"],
            activebackground=C["card"], activeforeground=C["green"],
            command=self._toggle_enable, bd=0, relief="flat",
            cursor="hand2",
        )
        self.toggle_btn.pack(side="right")

        coord_row = tk.Frame(self, bg=C["card"])
        coord_row.pack(fill="x", pady=(0, 8))

        self.coord_lbl = tk.Label(
            coord_row, text="X: \u2014   Y: \u2014",
            font=("Courier New", 11, "bold"),
            fg=C["text"], bg=C["card"], width=16, anchor="w"
        )
        self.coord_lbl.pack(side="left")

        pick_btn = tk.Button(
            coord_row, text="\u2295 PICK",
            font=("Courier New", 8, "bold"),
            fg=C["bg"], bg=C["accent"],
            activebackground=C["accent2"], activeforeground=C["bg"],
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            command=self._pick,
        )
        pick_btn.pack(side="right")

        opt_row = tk.Frame(self, bg=C["card"])
        opt_row.pack(fill="x")

        tk.Label(opt_row, text="BTN", font=("Courier New", 8),
                 fg=C["text2"], bg=C["card"]).pack(side="left")

        self.btn_var = tk.StringVar(value=spot.button)
        for val, lbl in [("left", "LEFT"), ("right", "RIGHT")]:
            rb = tk.Radiobutton(
                opt_row, text=lbl, variable=self.btn_var, value=val,
                font=("Courier New", 8, "bold"),
                fg=C["text"], bg=C["card"], selectcolor=C["card"],
                activebackground=C["card"], activeforeground=C["accent"],
                command=self._on_btn_change, relief="flat", bd=0,
                cursor="hand2", indicatoron=0,
                padx=6, pady=2,
            )
            rb.pack(side="left", padx=(6, 0))

        tk.Label(opt_row, text="  TYPE", font=("Courier New", 8),
                 fg=C["text2"], bg=C["card"]).pack(side="left", padx=(10, 0))

        self.type_var = tk.StringVar(value=spot.click_type)
        for val, lbl in [("single", "\xd71"), ("double", "\xd72")]:
            rb = tk.Radiobutton(
                opt_row, text=lbl, variable=self.type_var, value=val,
                font=("Courier New", 8, "bold"),
                fg=C["text"], bg=C["card"], selectcolor=C["card"],
                activebackground=C["card"], activeforeground=C["accent"],
                command=self._on_type_change, relief="flat", bd=0,
                cursor="hand2", indicatoron=0,
                padx=6, pady=2,
            )
            rb.pack(side="left", padx=(4, 0))

        self._refresh_state()

    def _toggle_enable(self):
        self.spot.enabled = self.enable_var.get()
        self._refresh_state()

    def _on_btn_change(self):
        self.spot.button = self.btn_var.get()

    def _on_type_change(self):
        self.spot.click_type = self.type_var.get()

    def _pick(self):
        if self.app.running:
            return
        self.app.root.iconify()
        time.sleep(0.2)
        PickOverlay(self.app.root, self._set_coords)

    def _set_coords(self, x, y):
        self.app.root.deiconify()
        if x is not None:
            self.spot.x, self.spot.y = x, y
            self.coord_lbl.config(text=f"X: {x}   Y: {y}")

    def _refresh_state(self):
        fg = C["text"] if self.spot.enabled else C["text3"]
        self.coord_lbl.config(fg=fg)


class FistClick:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FIST CLICK")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        try:
            if getattr(sys, "frozen", False):
                base = sys._MEIPASS
            else:
                base = os.path.dirname(__file__)
            ico = os.path.join(base, "icon.ico")
            if os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

        self.spots = [ClickSpot() for _ in range(MAX_SPOTS)]
        self.running = False
        self.click_thread = None
        self.hotkey = "f6"
        self.hotkey_listener = None

        self._build_ui()
        self._start_hotkey_listener()

        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _build_ui(self):
        root = self.root

        title_bar = tk.Frame(root, bg=C["bg"], pady=16)
        title_bar.pack(fill="x", padx=20)

        tk.Label(title_bar, text="FIST", font=("Courier New", 22, "bold"),
                 fg=C["accent"], bg=C["bg"]).pack(side="left")
        tk.Label(title_bar, text=" CLICK", font=("Courier New", 22, "bold"),
                 fg=C["text"], bg=C["bg"]).pack(side="left")

        self.status_dot = tk.Label(title_bar, text="\u25cf",
                                   font=("Courier New", 14), fg=C["text3"], bg=C["bg"])
        self.status_dot.pack(side="right", padx=(0, 4))
        self.status_lbl = tk.Label(title_bar, text="IDLE",
                                   font=("Courier New", 9, "bold"), fg=C["text3"], bg=C["bg"])
        self.status_lbl.pack(side="right")

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=20, pady=(0, 14))

        spots_frame = tk.Frame(root, bg=C["bg"])
        spots_frame.pack(fill="x", padx=20)

        tk.Label(spots_frame, text=f"CLICK SPOTS  (0/{MAX_SPOTS})",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(anchor="w", pady=(0, 8))

        self.spot_cards = []
        grid = tk.Frame(spots_frame, bg=C["bg"])
        grid.pack(fill="x")

        for i, spot in enumerate(self.spots):
            card = SpotCard(grid, i, spot, self)
            row, col = divmod(i, 2)
            card.grid(row=row, column=col,
                      padx=(0 if col == 0 else 6, 0),
                      pady=(0 if row == 0 else 6, 0), sticky="nsew")
            self.spot_cards.append(card)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=20, pady=14)

        settings = tk.Frame(root, bg=C["bg"])
        settings.pack(fill="x", padx=20)

        tk.Label(settings, text="SETTINGS", font=("Courier New", 8, "bold"),
                 fg=C["text2"], bg=C["bg"]).pack(anchor="w", pady=(0, 8))

        # Interval row
        ivl_row = tk.Frame(settings, bg=C["bg"])
        ivl_row.pack(fill="x", pady=(0, 8))
        tk.Label(ivl_row, text="INTERVAL", font=("Courier New", 8, "bold"),
                 fg=C["text2"], bg=C["bg"], width=12, anchor="w").pack(side="left")
        self.interval_h = self._spin(ivl_row, 0, 23, "h")
        tk.Label(ivl_row, text=":", fg=C["text2"], bg=C["bg"],
                 font=("Courier New", 11)).pack(side="left")
        self.interval_m = self._spin(ivl_row, 0, 59, "m")
        tk.Label(ivl_row, text=":", fg=C["text2"], bg=C["bg"],
                 font=("Courier New", 11)).pack(side="left")
        self.interval_s = self._spin(ivl_row, 0, 59, "s", default=1)
        tk.Label(ivl_row, text=":", fg=C["text2"], bg=C["bg"],
                 font=("Courier New", 11)).pack(side="left")
        self.interval_ms = self._spin(ivl_row, 0, 999, "ms")

        # Duration mode
        mode_row = tk.Frame(settings, bg=C["bg"])
        mode_row.pack(fill="x", pady=(0, 8))
        tk.Label(mode_row, text="DURATION", font=("Courier New", 8, "bold"),
                 fg=C["text2"], bg=C["bg"], width=12, anchor="w").pack(side="left")
        self.time_mode = tk.StringVar(value="infinite")
        for val, lbl, px in [("infinite", "INFINITE", 0), ("timer", "TIMER", 6)]:
            tk.Radiobutton(
                mode_row, text=lbl, variable=self.time_mode, value=val,
                font=("Courier New", 8, "bold"), fg=C["text"], bg=C["bg"],
                selectcolor=C["bg"], activebackground=C["bg"],
                relief="flat", bd=0, cursor="hand2", indicatoron=0, padx=8, pady=3,
            ).pack(side="left", padx=(px, 0))

        # Timer duration
        tmr_row = tk.Frame(settings, bg=C["bg"])
        tmr_row.pack(fill="x", pady=(0, 8))
        tk.Label(tmr_row, text="TIMER DUR.", font=("Courier New", 8, "bold"),
                 fg=C["text2"], bg=C["bg"], width=12, anchor="w").pack(side="left")
        self.timer_h = self._spin(tmr_row, 0, 23, "h")
        tk.Label(tmr_row, text=":", fg=C["text2"], bg=C["bg"],
                 font=("Courier New", 11)).pack(side="left")
        self.timer_m = self._spin(tmr_row, 0, 59, "m")
        tk.Label(tmr_row, text=":", fg=C["text2"], bg=C["bg"],
                 font=("Courier New", 11)).pack(side="left")
        self.timer_s = self._spin(tmr_row, 0, 59, "s", default=5)

        # Hotkey
        hk_row = tk.Frame(settings, bg=C["bg"])
        hk_row.pack(fill="x", pady=(0, 4))
        tk.Label(hk_row, text="HOTKEY", font=("Courier New", 8, "bold"),
                 fg=C["text2"], bg=C["bg"], width=12, anchor="w").pack(side="left")
        self.hk_display = tk.Label(hk_row, text="F6",
                                   font=("Courier New", 10, "bold"),
                                   fg=C["accent"], bg=C["card"], padx=10, pady=4, relief="flat")
        self.hk_display.pack(side="left")
        self.hk_btn = tk.Button(hk_row, text="SET",
                                font=("Courier New", 8, "bold"),
                                fg=C["text"], bg=C["inactive"],
                                activebackground=C["hover"], activeforeground=C["text"],
                                relief="flat", bd=0, padx=8, pady=3,
                                cursor="hand2", command=self._set_hotkey)
        self.hk_btn.pack(side="left", padx=(8, 0))

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=20, pady=14)

        # Controls
        ctrl = tk.Frame(root, bg=C["bg"], pady=4)
        ctrl.pack(fill="x", padx=20, pady=(0, 20))

        self.start_btn = tk.Button(ctrl, text="\u25b6  START",
                                   font=("Courier New", 12, "bold"),
                                   fg=C["bg"], bg=C["green"],
                                   activebackground="#25A244", activeforeground=C["bg"],
                                   relief="flat", bd=0, padx=0, pady=12,
                                   cursor="hand2", command=self._start)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.stop_btn = tk.Button(ctrl, text="\u25a0  STOP",
                                  font=("Courier New", 12, "bold"),
                                  fg=C["bg"], bg=C["accent"],
                                  activebackground="#CC2D24", activeforeground=C["bg"],
                                  relief="flat", bd=0, padx=0, pady=12,
                                  cursor="hand2", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", fill="x", expand=True)

        self.click_count = 0
        self.counter_lbl = tk.Label(root, text="CLICKS: 0",
                                    font=("Courier New", 8),
                                    fg=C["text3"], bg=C["bg"])
        self.counter_lbl.pack(pady=(0, 12))

    def _spin(self, parent, from_, to, label, default=0):
        frame = tk.Frame(parent, bg=C["bg"])
        frame.pack(side="left")
        var = tk.StringVar(value=str(default).zfill(2 if to < 100 else 3))
        sb = tk.Spinbox(frame, from_=from_, to=to, textvariable=var, width=3,
                        font=("Courier New", 11, "bold"),
                        fg=C["text"], bg=C["card"], insertbackground=C["text"],
                        buttonbackground=C["inactive"],
                        relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1,
                        format="%02.0f" if to < 100 else "%03.0f")
        sb.pack()
        tk.Label(frame, text=label, font=("Courier New", 7),
                 fg=C["text3"], bg=C["bg"]).pack()
        return var

    def _set_hotkey(self):
        self.hk_display.config(text="\u2026", fg=C["text2"])
        self.hk_btn.config(state="disabled")
        self.root.bind("<KeyPress>", self._capture_key)
        self.root.focus_force()

    def _capture_key(self, event):
        self.root.unbind("<KeyPress>")
        self.hotkey = event.keysym.lower()
        self.hk_display.config(text=event.keysym.upper(), fg=C["accent"])
        self.hk_btn.config(state="normal")
        self._start_hotkey_listener()

    def _start_hotkey_listener(self):
        if not PYNPUT_OK:
            return
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass

        def on_press(key):
            try:
                name = key.name.lower() if hasattr(key, "name") else str(key).lower()
            except Exception:
                name = str(key).lower()
            if name == self.hotkey:
                self.root.after(0, self._toggle)

        self.hotkey_listener = pynkeyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        active = [s for s in self.spots if s.enabled and s.x is not None]
        if not active:
            self._flash_error("No active spots with coordinates!")
            return
        if not PYAUTOGUI_OK:
            self._flash_error("pyautogui not available!")
            return
        self.running = True
        self.click_count = 0
        self._set_ui_running(True)
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()

    def _stop(self):
        self.running = False
        self._set_ui_running(False)

    def _set_ui_running(self, running: bool):
        if running:
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_dot.config(fg=C["green"])
            self.status_lbl.config(text="RUNNING", fg=C["green"])
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_dot.config(fg=C["text3"])
            self.status_lbl.config(text="IDLE", fg=C["text3"])

    def _flash_error(self, msg):
        self.status_lbl.config(text=msg, fg=C["accent"])
        self.status_dot.config(fg=C["accent"])
        self.root.after(2500, lambda: (
            self.status_lbl.config(text="IDLE", fg=C["text3"]),
            self.status_dot.config(fg=C["text3"])
        ))

    def _click_loop(self):
        try:
            ih = int(self.interval_h.get())
            im = int(self.interval_m.get())
            is_ = int(self.interval_s.get())
            ims = int(self.interval_ms.get())
        except ValueError:
            ih = im = ims = 0
            is_ = 1
        interval = ih * 3600 + im * 60 + is_ + ims / 1000.0
        if interval <= 0:
            interval = 0.05

        use_timer = (self.time_mode.get() == "timer")
        if use_timer:
            try:
                th = int(self.timer_h.get())
                tm = int(self.timer_m.get())
                ts = int(self.timer_s.get())
            except ValueError:
                th = tm = 0
                ts = 5
            end_time = time.time() + th * 3600 + tm * 60 + ts
        else:
            end_time = None

        active = [s for s in self.spots if s.enabled and s.x is not None]

        while self.running:
            if end_time and time.time() >= end_time:
                self.root.after(0, self._stop)
                break
            for spot in active:
                if not self.running:
                    break
                try:
                    if spot.click_type == "double":
                        pyautogui.doubleClick(spot.x, spot.y, button=spot.button)
                    else:
                        pyautogui.click(spot.x, spot.y, button=spot.button)
                    self.click_count += 1
                except Exception:
                    pass
            self.root.after(0, self._update_counter)
            time.sleep(interval)

    def _update_counter(self):
        self.counter_lbl.config(text=f"CLICKS: {self.click_count:,}")

    def _on_close(self):
        self.running = False
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    FistClick()
