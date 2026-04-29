# -*- coding: utf-8 -*-
"""
FIST CLICK v2.0.0
Auto Clicker — Multi-spot, Script mode, Follow-mouse, Settings, i18n
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, filedialog, messagebox, colorchooser
import threading
import time
import sys
import os
import json
import ctypes

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    PYAUTOGUI_OK = True
except Exception:
    PYAUTOGUI_OK = False

try:
    from pynput import keyboard as pynkeyboard
    PYNPUT_OK = True
except Exception:
    PYNPUT_OK = False

# ── Config path ───────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(_BASE, "fist_click_config.json")

# ── i18n strings ─────────────────────────────────────────────────────────────
STR = {
    "ru": {
        "title": "FIST CLICK",
        "tab_spots": "СПОТЫ",
        "tab_follow": "ПО МЫШИ",
        "tab_script": "СКРИПТ",
        "tab_settings": "НАСТРОЙКИ",
        "spots_label": "ТОЧКИ КЛИКОВ",
        "spot": "СПОТ",
        "btn_left": "ЛЕВАЯ",
        "btn_right": "ПРАВАЯ",
        "type_single": "×1",
        "type_double": "×2",
        "pick": "⊕ ВЫБРАТЬ",
        "on": "ВКЛ",
        "interval": "ИНТЕРВАЛ",
        "duration": "РЕЖИМ",
        "infinite": "БЕСКОНЕЧНО",
        "timer": "ТАЙМЕР",
        "timer_dur": "ДЛИТ. ТАЙМЕРА",
        "hotkey": "ГОРЯЧАЯ КЛАВИША",
        "set": "НАЗНАЧИТЬ",
        "clear": "СБРОСИТЬ",
        "start": "▶  СТАРТ",
        "stop": "■  СТОП",
        "clicks": "КЛИКОВ",
        "idle": "ОЖИДАНИЕ",
        "running": "РАБОТАЕТ",
        "follow_title": "РЕЖИМ: СЛЕДОВАТЬ ЗА МЫШЬЮ",
        "follow_desc": "Кликает по текущей позиции курсора. Интервал и тип клика берутся из главных настроек.",
        "follow_btn": "КНОПКА",
        "follow_type": "ТИП",
        "script_title": "СКРИПТОВЫЙ РЕЖИМ",
        "script_desc": "Добавьте шаги — координаты, задержка, кнопка, тип. Выполняются по порядку.",
        "sc_add": "+ ДОБАВИТЬ ШАГ",
        "sc_del": "− УДАЛИТЬ",
        "sc_up": "↑",
        "sc_dn": "↓",
        "sc_pick": "ВЫБРАТЬ",
        "sc_delay": "Задержка (мс)",
        "sc_loops": "Повторений (0=∞)",
        "sc_col_n": "#",
        "sc_col_x": "X",
        "sc_col_y": "Y",
        "sc_col_btn": "Кнопка",
        "sc_col_type": "Тип",
        "sc_col_delay": "Задержка мс",
        "set_lang": "ЯЗЫК",
        "set_topmost": "Поверх всех окон",
        "set_hotkey_start": "Горячая кл. СТАРТ/СТОП",
        "set_font": "ШРИФТ",
        "set_font_size": "Размер шрифта",
        "set_font_system": "Системные шрифты",
        "set_font_load": "Загрузить .ttf/.otf",
        "set_theme": "ТЕМА",
        "set_bg": "Фон",
        "set_accent": "Акцент",
        "set_save": "СОХРАНИТЬ",
        "set_reset": "СБРОС",
        "pick_hint": "🎯  Кликните в нужное место  •  ESC — отмена",
        "no_spots": "Нет активных спотов с координатами!",
        "no_pyautogui": "pyautogui недоступен!",
        "press_key": "Нажмите клавишу...",
        "saved": "Настройки сохранены",
    },
    "en": {
        "title": "FIST CLICK",
        "tab_spots": "SPOTS",
        "tab_follow": "FOLLOW",
        "tab_script": "SCRIPT",
        "tab_settings": "SETTINGS",
        "spots_label": "CLICK SPOTS",
        "spot": "SPOT",
        "btn_left": "LEFT",
        "btn_right": "RIGHT",
        "type_single": "×1",
        "type_double": "×2",
        "pick": "⊕ PICK",
        "on": "ON",
        "interval": "INTERVAL",
        "duration": "DURATION",
        "infinite": "INFINITE",
        "timer": "TIMER",
        "timer_dur": "TIMER DUR.",
        "hotkey": "HOTKEY",
        "set": "SET",
        "clear": "CLEAR",
        "start": "▶  START",
        "stop": "■  STOP",
        "clicks": "CLICKS",
        "idle": "IDLE",
        "running": "RUNNING",
        "follow_title": "MODE: FOLLOW MOUSE",
        "follow_desc": "Clicks at the current cursor position. Interval and type are taken from main settings.",
        "follow_btn": "BUTTON",
        "follow_type": "TYPE",
        "script_title": "SCRIPT MODE",
        "script_desc": "Add steps — coordinates, delay, button, type. Executed in order.",
        "sc_add": "+ ADD STEP",
        "sc_del": "− DELETE",
        "sc_up": "↑",
        "sc_dn": "↓",
        "sc_pick": "PICK",
        "sc_delay": "Delay (ms)",
        "sc_loops": "Repeats (0=∞)",
        "sc_col_n": "#",
        "sc_col_x": "X",
        "sc_col_y": "Y",
        "sc_col_btn": "Button",
        "sc_col_type": "Type",
        "sc_col_delay": "Delay ms",
        "set_lang": "LANGUAGE",
        "set_topmost": "Always on top",
        "set_hotkey_start": "Hotkey START/STOP",
        "set_font": "FONT",
        "set_font_size": "Font size",
        "set_font_system": "System fonts",
        "set_font_load": "Load .ttf/.otf",
        "set_theme": "THEME",
        "set_bg": "Background",
        "set_accent": "Accent",
        "set_save": "SAVE",
        "set_reset": "RESET",
        "pick_hint": "🎯  Click to pick location  •  ESC — cancel",
        "no_spots": "No active spots with coordinates!",
        "no_pyautogui": "pyautogui not available!",
        "press_key": "Press a key...",
        "saved": "Settings saved",
    },
}

# ── Default config ────────────────────────────────────────────────────────────
DEFAULT_CFG = {
    "lang": "ru",
    "topmost": True,
    "hotkey": "f6",
    "font_family": "Courier New",
    "font_size": 9,
    "bg": "#181A20",
    "card": "#22252E",
    "border": "#313540",
    "accent": "#FF3B30",
    "green": "#30D158",
    "text": "#EAEAEA",
    "text2": "#8A8A8E",
    "text3": "#48484A",
    "bar_bg": "#2C2C2E",
}

MAX_SPOTS = 4


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = dict(DEFAULT_CFG)
        cfg.update(data)
        return cfg
    except Exception:
        return dict(DEFAULT_CFG)


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Data classes ──────────────────────────────────────────────────────────────
class ClickSpot:
    def __init__(self):
        self.x = None
        self.y = None
        self.enabled = True
        self.button = "left"
        self.click_type = "single"


class ScriptStep:
    def __init__(self, x=0, y=0, button="left", click_type="single", delay_ms=200):
        self.x = x
        self.y = y
        self.button = button
        self.click_type = click_type
        self.delay_ms = delay_ms


# ── Pick overlay ──────────────────────────────────────────────────────────────
class PickOverlay:
    def __init__(self, root, callback, hint=""):
        self.callback = callback
        self.win = tk.Toplevel(root)
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.01)
        self.win.attributes("-topmost", True)
        self.win.config(cursor="crosshair", bg="#000000")
        if hint:
            tk.Label(self.win, text=hint,
                     font=("Courier New", 12, "bold"),
                     fg="#FFFFFF", bg="#1A1A1A",
                     padx=20, pady=10).place(relx=0.5, rely=0.5, anchor="center")
        self.win.bind("<Button-1>", self._click)
        self.win.bind("<Escape>", self._cancel)
        self.win.focus_force()

    def _click(self, e):
        self.win.destroy()
        self.callback(e.x_root, e.y_root)

    def _cancel(self, e=None):
        self.win.destroy()
        self.callback(None, None)


# ── Progress bar ──────────────────────────────────────────────────────────────
class GradBar(tk.Canvas):
    def __init__(self, parent, accent, **kw):
        bg = kw.pop("bg", "#2C2C2E")
        super().__init__(parent, height=4, bg=bg, highlightthickness=0, **kw)
        self._pct = 0.0
        self._accent = accent
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, pct):
        self._pct = max(0.0, min(1.0, pct))
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        filled = int(w * self._pct)
        if filled <= 0:
            return
        # Parse accent color
        try:
            r0 = int(self._accent[1:3], 16)
            g0 = int(self._accent[3:5], 16)
            b0 = int(self._accent[5:7], 16)
        except Exception:
            r0, g0, b0 = 0xFF, 0x3B, 0x30
        for x in range(filled):
            t = x / max(w, 1)
            r = int(r0 * (1 - t) + 0x30 * t)
            g = int(g0 * (1 - t) + 0xD1 * t)
            b = int(b0 * (1 - t) + 0x58 * t)
            self.create_line(x, 0, x, 4, fill=f"#{r:02x}{g:02x}{b:02x}")


# ── Main application ──────────────────────────────────────────────────────────
class FistClick:
    def __init__(self):
        self.cfg = load_config()
        self._lang = self.cfg.get("lang", "ru")
        self.spots = [ClickSpot() for _ in range(MAX_SPOTS)]
        self.script_steps: list[ScriptStep] = []
        self.running = False
        self.click_thread = None
        self.hotkey = self.cfg.get("hotkey", "f6")
        self.hotkey_listener = None
        self._mode = "spots"   # spots | follow | script
        self._follow_btn = tk.StringVar()
        self._follow_type = tk.StringVar()
        self._time_mode = tk.StringVar()

        self.root = tk.Tk()
        self._apply_theme()
        self.root.title(self.t("title"))
        self.root.resizable(False, False)
        self.root.attributes("-topmost", self.cfg.get("topmost", True))
        self._build()
        self._start_hk_listener()
        self._center()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.mainloop()

    # ── helpers ───────────────────────────────────────────────────────────────
    def t(self, key):
        return STR.get(self._lang, STR["ru"]).get(key, key)

    def C(self, key):
        return self.cfg.get(key, DEFAULT_CFG.get(key, "#888888"))

    def _apply_theme(self):
        self.root.configure(bg=self.C("bg")) if hasattr(self, "root") and self.root.winfo_exists() else None

    def _font(self, size=None, bold=False):
        fam = self.cfg.get("font_family", "Courier New")
        sz  = size or self.cfg.get("font_size", 9)
        w   = "bold" if bold else "normal"
        return (fam, sz, w)

    def _center(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _sep(self, parent):
        tk.Frame(parent, bg=self.C("border"), height=1).pack(fill="x", padx=20, pady=8)

    def _lbl(self, parent, key, size=None, bold=False, fg=None, **kw):
        return tk.Label(parent, text=self.t(key),
                        font=self._font(size, bold),
                        fg=fg or self.C("text2"),
                        bg=self.C("bg"), **kw)

    def _btn(self, parent, key, cmd, bg=None, fg=None, pad=8, **kw):
        return tk.Button(parent,
                         text=self.t(key),
                         font=self._font(bold=True),
                         fg=fg or self.C("bg"),
                         bg=bg or self.C("accent"),
                         activebackground=self.C("border"),
                         activeforeground=self.C("text"),
                         relief="flat", bd=0, padx=pad, pady=4,
                         cursor="hand2", command=cmd, **kw)

    def _radio(self, parent, text, var, val, cmd=None, **kw):
        return tk.Radiobutton(parent, text=text, variable=var, value=val,
                              font=self._font(bold=True),
                              fg=self.C("text"), bg=self.C("card"),
                              selectcolor=self.C("accent"),
                              activebackground=self.C("card"),
                              relief="flat", bd=0, cursor="hand2",
                              indicatoron=0, padx=6, pady=2,
                              command=cmd, **kw)

    def _spin(self, parent, from_, to, label, default=0):
        frame = tk.Frame(parent, bg=self.C("bg"))
        frame.pack(side="left")
        var = tk.StringVar(value=str(default).zfill(2 if to < 100 else 3))
        sb = tk.Spinbox(frame, from_=from_, to=to, textvariable=var,
                        width=3, font=self._font(bold=True),
                        fg=self.C("text"), bg=self.C("card"),
                        insertbackground=self.C("text"),
                        buttonbackground=self.C("border"),
                        relief="flat", bd=1,
                        highlightbackground=self.C("border"),
                        highlightthickness=1,
                        format="%02.0f" if to < 100 else "%03.0f")
        sb.pack()
        tk.Label(frame, text=label, font=self._font(7),
                 fg=self.C("text3"), bg=self.C("bg")).pack()
        return var

    # ── build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        bg  = self.C("bg")
        card = self.C("card")
        root = self.root
        root.configure(bg=bg)

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = tk.Frame(root, bg=bg, pady=14)
        title_bar.pack(fill="x", padx=20)

        tk.Label(title_bar, text="FIST",
                 font=self._font(22, True), fg=self.C("accent"), bg=bg).pack(side="left")
        tk.Label(title_bar, text=" CLICK",
                 font=self._font(22, True), fg=self.C("text"), bg=bg).pack(side="left")
        tk.Label(title_bar, text="  v2.0",
                 font=self._font(8), fg=self.C("text3"), bg=bg).pack(side="left", pady=(8,0))

        self._status_dot = tk.Label(title_bar, text="●",
                                    font=self._font(13), fg=self.C("text3"), bg=bg)
        self._status_dot.pack(side="right", padx=(0,4))
        self._status_lbl = tk.Label(title_bar, text=self.t("idle"),
                                    font=self._font(8, True), fg=self.C("text3"), bg=bg)
        self._status_lbl.pack(side="right")

        self._sep(root)

        # ── Tab bar ───────────────────────────────────────────────────────────
        tab_bar = tk.Frame(root, bg=bg)
        tab_bar.pack(fill="x", padx=20, pady=(0,10))

        self._tab_btns = {}
        self._tabs = {}
        for key, lbl_key in [("spots", "tab_spots"), ("follow", "tab_follow"),
                              ("script", "tab_script"), ("settings", "tab_settings")]:
            b = tk.Button(tab_bar, text=self.t(lbl_key),
                          font=self._font(8, True),
                          relief="flat", bd=0, padx=12, pady=6,
                          cursor="hand2",
                          command=lambda k=key: self._show_tab(k))
            b.pack(side="left", padx=(0,2))
            self._tab_btns[key] = b

        # ── Content frame ─────────────────────────────────────────────────────
        self._content = tk.Frame(root, bg=bg)
        self._content.pack(fill="both", expand=True, padx=0)

        self._build_spots_tab()
        self._build_follow_tab()
        self._build_script_tab()
        self._build_settings_tab()

        self._show_tab("spots")

        # ── Bottom bar ────────────────────────────────────────────────────────
        self._sep(root)
        ctrl = tk.Frame(root, bg=bg)
        ctrl.pack(fill="x", padx=20, pady=(0,6))

        self._start_btn = tk.Button(ctrl, text=self.t("start"),
                                    font=self._font(12, True),
                                    fg=self.C("bg"), bg=self.C("green"),
                                    activebackground="#25A244",
                                    activeforeground=self.C("bg"),
                                    relief="flat", bd=0, pady=11,
                                    cursor="hand2", command=self._start)
        self._start_btn.pack(side="left", fill="x", expand=True, padx=(0,6))

        self._stop_btn = tk.Button(ctrl, text=self.t("stop"),
                                   font=self._font(12, True),
                                   fg=self.C("bg"), bg=self.C("accent"),
                                   activebackground="#CC2D24",
                                   activeforeground=self.C("bg"),
                                   relief="flat", bd=0, pady=11,
                                   cursor="hand2", command=self._stop,
                                   state="disabled")
        self._stop_btn.pack(side="left", fill="x", expand=True)

        self._click_count = 0
        self._counter_lbl = tk.Label(root,
                                     text=f"{self.t('clicks')}: 0",
                                     font=self._font(7),
                                     fg=self.C("text3"), bg=bg)
        self._counter_lbl.pack(pady=(2, 10))

    # ── SPOTS TAB ─────────────────────────────────────────────────────────────
    def _build_spots_tab(self):
        bg = self.C("bg")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["spots"] = f

        tk.Label(f, text=self.t("spots_label"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg
                 ).pack(anchor="w", padx=20, pady=(4,6))

        grid = tk.Frame(f, bg=bg)
        grid.pack(fill="x", padx=20)
        self._spot_cards = []
        for i, spot in enumerate(self.spots):
            card = self._make_spot_card(grid, i, spot)
            row, col = divmod(i, 2)
            card.grid(row=row, column=col,
                      padx=(0 if col==0 else 5, 0),
                      pady=(0 if row==0 else 5, 0),
                      sticky="nsew")
            self._spot_cards.append(card)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._sep(f)
        self._build_common_settings(f)

    def _make_spot_card(self, parent, index, spot):
        bg   = self.C("card")
        bdr  = self.C("border")
        card = tk.Frame(parent, bg=bg, padx=10, pady=8,
                        highlightbackground=bdr, highlightthickness=1)

        # Header
        hdr = tk.Frame(card, bg=bg)
        hdr.pack(fill="x", pady=(0,6))
        tk.Label(hdr, text=f"{self.t('spot')} {index+1}",
                 font=self._font(8, True), fg=self.C("accent"), bg=bg).pack(side="left")

        en_var = tk.BooleanVar(value=spot.enabled)
        tk.Checkbutton(hdr, variable=en_var, text=self.t("on"),
                       font=self._font(7, True),
                       fg=self.C("green"), bg=bg, selectcolor=bg,
                       activebackground=bg, bd=0, relief="flat", cursor="hand2",
                       command=lambda: self._toggle_spot(spot, en_var)
                       ).pack(side="right")

        # Coords
        crow = tk.Frame(card, bg=bg)
        crow.pack(fill="x", pady=(0,6))
        coord_lbl = tk.Label(crow, text="X: —   Y: —",
                             font=self._font(10, True),
                             fg=self.C("text"), bg=bg, width=14, anchor="w")
        coord_lbl.pack(side="left")
        tk.Button(crow, text=self.t("pick"),
                  font=self._font(7, True),
                  fg=self.C("bg"), bg=self.C("accent"),
                  activebackground=self.C("border"),
                  relief="flat", bd=0, padx=6, pady=2,
                  cursor="hand2",
                  command=lambda s=spot, cl=coord_lbl: self._pick_spot(s, cl)
                  ).pack(side="right")

        # Options row
        opt = tk.Frame(card, bg=bg)
        opt.pack(fill="x")
        tk.Label(opt, text="BTN", font=self._font(7),
                 fg=self.C("text2"), bg=bg).pack(side="left")

        btn_var = tk.StringVar(value=spot.button)
        for val, lbl in [("left", self.t("btn_left")), ("right", self.t("btn_right"))]:
            self._radio(opt, lbl, btn_var, val,
                        cmd=lambda v=btn_var, s=spot: setattr(s, "button", v.get())
                        ).pack(side="left", padx=(4,0))

        tk.Label(opt, text="  ×", font=self._font(7),
                 fg=self.C("text2"), bg=bg).pack(side="left", padx=(8,0))

        type_var = tk.StringVar(value=spot.click_type)
        for val, lbl in [("single", self.t("type_single")), ("double", self.t("type_double"))]:
            self._radio(opt, lbl, type_var, val,
                        cmd=lambda v=type_var, s=spot: setattr(s, "click_type", v.get())
                        ).pack(side="left", padx=(3,0))

        return card

    def _toggle_spot(self, spot, var):
        spot.enabled = var.get()

    def _pick_spot(self, spot, lbl):
        if self.running:
            return
        self.root.iconify()
        time.sleep(0.15)
        PickOverlay(self.root, lambda x, y: self._set_spot_coord(spot, lbl, x, y),
                    hint=self.t("pick_hint"))

    def _set_spot_coord(self, spot, lbl, x, y):
        self.root.deiconify()
        if x is not None:
            spot.x, spot.y = x, y
            lbl.config(text=f"X: {x}   Y: {y}")

    # ── FOLLOW TAB ────────────────────────────────────────────────────────────
    def _build_follow_tab(self):
        bg = self.C("bg")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["follow"] = f

        tk.Label(f, text=self.t("follow_title"),
                 font=self._font(10, True), fg=self.C("accent"), bg=bg
                 ).pack(anchor="w", padx=20, pady=(10,4))
        tk.Label(f, text=self.t("follow_desc"),
                 font=self._font(8), fg=self.C("text2"), bg=bg,
                 wraplength=420, justify="left"
                 ).pack(anchor="w", padx=20, pady=(0,12))

        card = tk.Frame(f, bg=self.C("card"),
                        highlightbackground=self.C("border"), highlightthickness=1)
        card.pack(fill="x", padx=20, pady=(0,10))
        inner = tk.Frame(card, bg=self.C("card"), padx=12, pady=10)
        inner.pack(fill="x")

        # Button
        row1 = tk.Frame(inner, bg=self.C("card"))
        row1.pack(fill="x", pady=(0,6))
        tk.Label(row1, text=self.t("follow_btn"),
                 font=self._font(8, True), fg=self.C("text2"),
                 bg=self.C("card"), width=10, anchor="w").pack(side="left")
        self._follow_btn.set("left")
        for val, lbl in [("left", self.t("btn_left")), ("right", self.t("btn_right"))]:
            self._radio(inner if False else row1, lbl, self._follow_btn, val
                        ).pack(side="left", padx=(4,0))

        # Type
        row2 = tk.Frame(inner, bg=self.C("card"))
        row2.pack(fill="x")
        tk.Label(row2, text=self.t("follow_type"),
                 font=self._font(8, True), fg=self.C("text2"),
                 bg=self.C("card"), width=10, anchor="w").pack(side="left")
        self._follow_type.set("single")
        for val, lbl in [("single", self.t("type_single")), ("double", self.t("type_double"))]:
            self._radio(row2, lbl, self._follow_type, val
                        ).pack(side="left", padx=(4,0))

        self._sep(f)
        self._build_common_settings(f)

    # ── SCRIPT TAB ────────────────────────────────────────────────────────────
    def _build_script_tab(self):
        bg = self.C("bg")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["script"] = f

        tk.Label(f, text=self.t("script_title"),
                 font=self._font(10, True), fg=self.C("accent"), bg=bg
                 ).pack(anchor="w", padx=20, pady=(10,4))
        tk.Label(f, text=self.t("script_desc"),
                 font=self._font(8), fg=self.C("text2"), bg=bg,
                 wraplength=420, justify="left"
                 ).pack(anchor="w", padx=20, pady=(0,8))

        # Toolbar
        tb = tk.Frame(f, bg=bg)
        tb.pack(fill="x", padx=20, pady=(0,6))
        for key, cmd in [("sc_add", self._sc_add), ("sc_del", self._sc_del),
                         ("sc_up", self._sc_up), ("sc_dn", self._sc_dn)]:
            tk.Button(tb, text=self.t(key),
                      font=self._font(8, True),
                      fg=self.C("text"), bg=self.C("card"),
                      activebackground=self.C("border"),
                      relief="flat", bd=0, padx=10, pady=4,
                      cursor="hand2", command=cmd
                      ).pack(side="left", padx=(0,4))

        # Table frame
        tbl_frame = tk.Frame(f, bg=self.C("card"),
                             highlightbackground=self.C("border"), highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0,8))

        cols = ("n", "x", "y", "btn", "type", "delay")
        col_keys = ("sc_col_n", "sc_col_x", "sc_col_y",
                    "sc_col_btn", "sc_col_type", "sc_col_delay")
        col_w = (30, 60, 60, 70, 60, 80)

        style = ttk.Style()
        style.configure("Script.Treeview",
                        background=self.C("card"),
                        foreground=self.C("text"),
                        fieldbackground=self.C("card"),
                        rowheight=24,
                        font=self._font())
        style.configure("Script.Treeview.Heading",
                        background=self.C("border"),
                        foreground=self.C("text2"),
                        font=self._font(bold=True))
        style.map("Script.Treeview",
                  background=[("selected", self.C("accent"))],
                  foreground=[("selected", "white")])

        self._sc_tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                     height=6, style="Script.Treeview")
        for c, k, w in zip(cols, col_keys, col_w):
            self._sc_tree.heading(c, text=self.t(k))
            self._sc_tree.column(c, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical",
                           command=self._sc_tree.yview)
        self._sc_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._sc_tree.pack(fill="both", expand=True)

        # Loops
        lp_row = tk.Frame(f, bg=bg)
        lp_row.pack(fill="x", padx=20, pady=(0,6))
        tk.Label(lp_row, text=self.t("sc_loops"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0,8))
        self._sc_loops_var = tk.StringVar(value="1")
        tk.Spinbox(lp_row, from_=0, to=9999, textvariable=self._sc_loops_var,
                   width=6, font=self._font(),
                   fg=self.C("text"), bg=self.C("card"),
                   insertbackground=self.C("text"),
                   relief="flat", bd=1,
                   highlightbackground=self.C("border"),
                   highlightthickness=1
                   ).pack(side="left")

        self._sep(f)
        self._build_common_settings(f)

    def _sc_refresh(self):
        self._sc_tree.delete(*self._sc_tree.get_children())
        for i, s in enumerate(self.script_steps):
            self._sc_tree.insert("", "end", values=(
                i+1, s.x, s.y, s.button, s.click_type, s.delay_ms
            ))

    def _sc_add(self):
        self.root.iconify()
        time.sleep(0.15)
        PickOverlay(self.root, self._sc_picked, hint=self.t("pick_hint"))

    def _sc_picked(self, x, y):
        self.root.deiconify()
        if x is not None:
            self.script_steps.append(ScriptStep(x, y))
            self._sc_refresh()

    def _sc_sel_index(self):
        sel = self._sc_tree.selection()
        if not sel:
            return None
        return self._sc_tree.index(sel[0])

    def _sc_del(self):
        i = self._sc_sel_index()
        if i is not None and 0 <= i < len(self.script_steps):
            self.script_steps.pop(i)
            self._sc_refresh()

    def _sc_up(self):
        i = self._sc_sel_index()
        if i is not None and i > 0:
            self.script_steps[i-1], self.script_steps[i] = \
                self.script_steps[i], self.script_steps[i-1]
            self._sc_refresh()
            self._sc_tree.selection_set(self._sc_tree.get_children()[i-1])

    def _sc_dn(self):
        i = self._sc_sel_index()
        if i is not None and i < len(self.script_steps)-1:
            self.script_steps[i], self.script_steps[i+1] = \
                self.script_steps[i+1], self.script_steps[i]
            self._sc_refresh()
            self._sc_tree.selection_set(self._sc_tree.get_children()[i+1])

    # ── SETTINGS TAB ─────────────────────────────────────────────────────────
    def _build_settings_tab(self):
        bg = self.C("bg")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["settings"] = f

        canvas = tk.Canvas(f, bg=bg, highlightthickness=0)
        sb = tk.Scrollbar(f, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=bg)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<MouseWheel>",
                   lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        p = inner  # alias

        def sec(key):
            tk.Label(p, text=self.t(key),
                     font=self._font(8, True), fg=self.C("text2"), bg=bg
                     ).pack(anchor="w", padx=20, pady=(12,4))

        def row():
            r = tk.Frame(p, bg=bg)
            r.pack(fill="x", padx=20, pady=3)
            return r

        # Language
        sec("set_lang")
        lr = row()
        self._lang_var = tk.StringVar(value=self._lang)
        for val, lbl in [("ru", "Русский"), ("en", "English")]:
            tk.Radiobutton(lr, text=lbl, variable=self._lang_var, value=val,
                           font=self._font(),
                           fg=self.C("text"), bg=bg, selectcolor=bg,
                           activebackground=bg, relief="flat", bd=0, cursor="hand2"
                           ).pack(side="left", padx=(0,12))

        # Topmost
        sec("set_topmost")
        self._topmost_var = tk.BooleanVar(value=self.cfg.get("topmost", True))
        tr = row()
        tk.Checkbutton(tr, variable=self._topmost_var,
                       text=self.t("set_topmost"),
                       font=self._font(),
                       fg=self.C("text"), bg=bg, selectcolor=bg,
                       activebackground=bg, relief="flat", bd=0, cursor="hand2"
                       ).pack(side="left")

        # Hotkey
        sec("set_hotkey_start")
        hkr = row()
        self._hk_lbl = tk.Label(hkr, text=self.hotkey.upper(),
                                 font=self._font(bold=True),
                                 fg=self.C("accent"), bg=self.C("card"),
                                 padx=10, pady=4, relief="flat")
        self._hk_lbl.pack(side="left")
        self._hk_set_btn = tk.Button(hkr, text=self.t("set"),
                                     font=self._font(bold=True),
                                     fg=self.C("text"), bg=self.C("card"),
                                     activebackground=self.C("border"),
                                     relief="flat", bd=0, padx=8, pady=3,
                                     cursor="hand2", command=self._capture_hotkey)
        self._hk_set_btn.pack(side="left", padx=(6,0))
        tk.Button(hkr, text=self.t("clear"),
                  font=self._font(bold=True),
                  fg=self.C("text2"), bg=self.C("card"),
                  activebackground=self.C("border"),
                  relief="flat", bd=0, padx=8, pady=3,
                  cursor="hand2", command=self._clear_hotkey
                  ).pack(side="left", padx=(4,0))

        # Font
        sec("set_font")
        fr = row()
        tk.Label(fr, text=self.t("set_font_size"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0,6))
        self._font_size_var = tk.StringVar(value=str(self.cfg.get("font_size", 9)))
        tk.Spinbox(fr, from_=7, to=16, textvariable=self._font_size_var,
                   width=4, font=self._font(),
                   fg=self.C("text"), bg=self.C("card"),
                   insertbackground=self.C("text"),
                   relief="flat", bd=1,
                   highlightbackground=self.C("border"),
                   highlightthickness=1
                   ).pack(side="left")

        fr2 = row()
        tk.Label(fr2, text=self.t("set_font_system"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0,6))
        avail = list(tkfont.families())
        avail.sort()
        self._font_fam_var = tk.StringVar(value=self.cfg.get("font_family", "Courier New"))
        cb = ttk.Combobox(fr2, textvariable=self._font_fam_var,
                          values=avail, width=22, state="readonly")
        cb.pack(side="left")

        # Theme
        sec("set_theme")
        for cfg_key, lbl_key in [("bg", "set_bg"), ("accent", "set_accent")]:
            cr = row()
            tk.Label(cr, text=self.t(lbl_key),
                     font=self._font(8), fg=self.C("text2"), bg=bg,
                     width=16, anchor="w").pack(side="left")
            cur_color = self.cfg.get(cfg_key, DEFAULT_CFG[cfg_key])
            swatch = tk.Label(cr, bg=cur_color, width=4, relief="flat",
                              cursor="hand2")
            swatch.pack(side="left", padx=(0,6), ipady=8)
            swatch.bind("<Button-1>",
                        lambda e, k=cfg_key, sw=swatch: self._pick_color(k, sw))

        # Save / Reset
        tk.Frame(p, bg=self.C("border"), height=1).pack(fill="x", padx=20, pady=12)
        btn_row = row()
        tk.Button(btn_row, text=self.t("set_save"),
                  font=self._font(bold=True),
                  fg=self.C("bg"), bg=self.C("green"),
                  activebackground="#25A244",
                  relief="flat", bd=0, padx=16, pady=6,
                  cursor="hand2", command=self._save_settings
                  ).pack(side="left", padx=(0,8))
        tk.Button(btn_row, text=self.t("set_reset"),
                  font=self._font(bold=True),
                  fg=self.C("text"), bg=self.C("card"),
                  activebackground=self.C("border"),
                  relief="flat", bd=0, padx=16, pady=6,
                  cursor="hand2", command=self._reset_settings
                  ).pack(side="left")

    def _pick_color(self, key, swatch):
        cur = self.cfg.get(key, DEFAULT_CFG.get(key, "#888888"))
        result = colorchooser.askcolor(color=cur, title=key)
        if result and result[1]:
            self.cfg[key] = result[1]
            swatch.config(bg=result[1])

    def _capture_hotkey(self):
        self._hk_lbl.config(text=self.t("press_key"), fg=self.C("text2"))
        self._hk_set_btn.config(state="disabled")
        self.root.bind("<KeyPress>", self._on_key_capture)
        self.root.focus_force()

    def _on_key_capture(self, e):
        self.root.unbind("<KeyPress>")
        self.hotkey = e.keysym.lower()
        self._hk_lbl.config(text=e.keysym.upper(), fg=self.C("accent"))
        self._hk_set_btn.config(state="normal")
        self._start_hk_listener()

    def _clear_hotkey(self):
        self.hotkey = ""
        self._hk_lbl.config(text="—", fg=self.C("text3"))
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None

    def _save_settings(self):
        self.cfg["lang"] = self._lang_var.get()
        self.cfg["topmost"] = self._topmost_var.get()
        self.cfg["hotkey"] = self.hotkey
        try:
            self.cfg["font_size"] = int(self._font_size_var.get())
        except Exception:
            pass
        self.cfg["font_family"] = self._font_fam_var.get()
        save_config(self.cfg)
        # Apply topmost immediately
        self.root.attributes("-topmost", self.cfg["topmost"])
        self._start_hk_listener()
        messagebox.showinfo("FIST CLICK", self.t("saved"))

    def _reset_settings(self):
        self.cfg = dict(DEFAULT_CFG)
        save_config(self.cfg)
        messagebox.showinfo("FIST CLICK", self.t("saved"))

    # ── Common settings (interval, duration, hotkey display) ──────────────────
    def _build_common_settings(self, parent):
        bg = self.C("bg")

        # Interval
        ivl = tk.Frame(parent, bg=bg)
        ivl.pack(fill="x", padx=20, pady=(0,6))
        tk.Label(ivl, text=self.t("interval"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        self._ivl_h  = self._spin(ivl, 0, 23, "h")
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg,
                 font=self._font(11)).pack(side="left")
        self._ivl_m  = self._spin(ivl, 0, 59, "m")
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg,
                 font=self._font(11)).pack(side="left")
        self._ivl_s  = self._spin(ivl, 0, 59, "s", default=1)
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg,
                 font=self._font(11)).pack(side="left")
        self._ivl_ms = self._spin(ivl, 0, 999, "ms")

        # Duration mode
        dur = tk.Frame(parent, bg=bg)
        dur.pack(fill="x", padx=20, pady=(0,6))
        tk.Label(dur, text=self.t("duration"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        self._time_mode.set("infinite")
        for val, key in [("infinite", "infinite"), ("timer", "timer")]:
            tk.Radiobutton(dur, text=self.t(key), variable=self._time_mode, value=val,
                           font=self._font(bold=True),
                           fg=self.C("text"), bg=bg, selectcolor=bg,
                           activebackground=bg, relief="flat", bd=0,
                           cursor="hand2", indicatoron=0, padx=8, pady=3
                           ).pack(side="left", padx=(0,4))

        # Timer duration
        tmr = tk.Frame(parent, bg=bg)
        tmr.pack(fill="x", padx=20, pady=(0,6))
        tk.Label(tmr, text=self.t("timer_dur"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        self._tmr_h = self._spin(tmr, 0, 23, "h")
        tk.Label(tmr, text=":", fg=self.C("text2"), bg=bg,
                 font=self._font(11)).pack(side="left")
        self._tmr_m = self._spin(tmr, 0, 59, "m")
        tk.Label(tmr, text=":", fg=self.C("text2"), bg=bg,
                 font=self._font(11)).pack(side="left")
        self._tmr_s = self._spin(tmr, 0, 59, "s", default=10)

    # ── Tab switching ─────────────────────────────────────────────────────────
    def _show_tab(self, key):
        self._mode = key
        for k, f in self._tabs.items():
            f.pack_forget()
        self._tabs[key].pack(fill="both", expand=True)
        for k, b in self._tab_btns.items():
            if k == key:
                b.config(fg=self.C("accent"), bg=self.C("card"))
            else:
                b.config(fg=self.C("text2"), bg=self.C("bg"))

    # ── Hotkey listener ───────────────────────────────────────────────────────
    def _start_hk_listener(self):
        if not PYNPUT_OK or not self.hotkey:
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
                name = ""
            if name == self.hotkey:
                self.root.after(0, self._toggle)

        self.hotkey_listener = pynkeyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    # ── Start / Stop / Toggle ─────────────────────────────────────────────────
    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if not PYAUTOGUI_OK:
            self._flash(self.t("no_pyautogui"))
            return
        if self._mode == "spots":
            active = [s for s in self.spots if s.enabled and s.x is not None]
            if not active:
                self._flash(self.t("no_spots"))
                return
        elif self._mode == "script":
            if not self.script_steps:
                self._flash(self.t("no_spots"))
                return
        self.running = True
        self._click_count = 0
        self._set_ui_running(True)
        target = {
            "spots":  self._loop_spots,
            "follow": self._loop_follow,
            "script": self._loop_script,
        }[self._mode]
        self.click_thread = threading.Thread(target=target, daemon=True)
        self.click_thread.start()

    def _stop(self):
        self.running = False
        self._set_ui_running(False)

    def _set_ui_running(self, running):
        if running:
            self._start_btn.config(state="disabled")
            self._stop_btn.config(state="normal")
            self._status_dot.config(fg=self.C("green"))
            self._status_lbl.config(text=self.t("running"), fg=self.C("green"))
        else:
            self._start_btn.config(state="normal")
            self._stop_btn.config(state="disabled")
            self._status_dot.config(fg=self.C("text3"))
            self._status_lbl.config(text=self.t("idle"), fg=self.C("text3"))

    def _flash(self, msg):
        self._status_lbl.config(text=msg, fg=self.C("accent"))
        self._status_dot.config(fg=self.C("accent"))
        self.root.after(2500, lambda: (
            self._status_lbl.config(text=self.t("idle"), fg=self.C("text3")),
            self._status_dot.config(fg=self.C("text3"))
        ))

    def _update_counter(self):
        self._counter_lbl.config(
            text=f"{self.t('clicks')}: {self._click_count:,}")

    # ── Interval helper ───────────────────────────────────────────────────────
    def _get_interval(self):
        try:
            iv = (int(self._ivl_h.get()) * 3600 +
                  int(self._ivl_m.get()) * 60 +
                  int(self._ivl_s.get()) +
                  int(self._ivl_ms.get()) / 1000.0)
        except Exception:
            iv = 1.0
        return max(iv, 0.05)

    def _get_end_time(self):
        if self._time_mode.get() != "timer":
            return None
        try:
            dur = (int(self._tmr_h.get()) * 3600 +
                   int(self._tmr_m.get()) * 60 +
                   int(self._tmr_s.get()))
        except Exception:
            dur = 10
        return time.time() + max(dur, 1)

    # ── Click loops ───────────────────────────────────────────────────────────
    def _loop_spots(self):
        interval = self._get_interval()
        end_time = self._get_end_time()
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
                    self._click_count += 1
                except Exception:
                    pass
            self.root.after(0, self._update_counter)
            time.sleep(interval)

    def _loop_follow(self):
        interval = self._get_interval()
        end_time = self._get_end_time()
        btn  = self._follow_btn.get() or "left"
        typ  = self._follow_type.get() or "single"
        while self.running:
            if end_time and time.time() >= end_time:
                self.root.after(0, self._stop)
                break
            try:
                x, y = pyautogui.position()
                if typ == "double":
                    pyautogui.doubleClick(x, y, button=btn)
                else:
                    pyautogui.click(x, y, button=btn)
                self._click_count += 1
            except Exception:
                pass
            self.root.after(0, self._update_counter)
            time.sleep(interval)

    def _loop_script(self):
        end_time = self._get_end_time()
        try:
            loops = int(self._sc_loops_var.get())
        except Exception:
            loops = 1
        infinite = (loops == 0)
        iteration = 0
        while self.running:
            if end_time and time.time() >= end_time:
                self.root.after(0, self._stop)
                break
            if not infinite and iteration >= loops:
                self.root.after(0, self._stop)
                break
            for step in self.script_steps:
                if not self.running:
                    break
                try:
                    if step.click_type == "double":
                        pyautogui.doubleClick(step.x, step.y, button=step.button)
                    else:
                        pyautogui.click(step.x, step.y, button=step.button)
                    self._click_count += 1
                except Exception:
                    pass
                self.root.after(0, self._update_counter)
                time.sleep(step.delay_ms / 1000.0)
            iteration += 1

    # ── Close ─────────────────────────────────────────────────────────────────
    def _quit(self):
        self.running = False
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    FistClick()
