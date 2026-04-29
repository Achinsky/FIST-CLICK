# -*- coding: utf-8 -*-
"""
FIST CLICK v2.0.2
Auto Clicker — Multi-spot, Script mode, Follow-mouse, Macro Recorder, Settings, i18n
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, filedialog, messagebox, colorchooser
import threading
import time
import sys
import os
import json

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    PYAUTOGUI_OK = True
except Exception:
    PYAUTOGUI_OK = False

try:
    from pynput import keyboard as pynkeyboard, mouse as pynmouse
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
        "tab_record": "ЗАПИСЬ",
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
        "sc_delay": "Задержка (мс)",
        "sc_loops": "Повторений (0=∞)",
        "sc_col_n": "#",
        "sc_col_x": "X",
        "sc_col_y": "Y",
        "sc_col_btn": "Кнопка",
        "sc_col_type": "Тип",
        "sc_col_delay": "Задержка мс",
        # --- Record tab ---
        "rec_title": "ЗАПИСЬ ДЕЙСТВИЙ",
        "rec_desc": "Нажмите F6 чтобы начать запись всех действий (мышь, клавиатура, скролл). Нажмите F6 снова для остановки.",
        "rec_start": "⏺  НАЧАТЬ ЗАПИСЬ",
        "rec_stop_rec": "⏹  ОСТАНОВИТЬ ЗАПИСЬ",
        "rec_play": "▶  ВОСПРОИЗВЕСТИ",
        "rec_stop_play": "■  СТОП",
        "rec_clear": "🗑  ОЧИСТИТЬ",
        "rec_events": "ЗАПИСАННЫЕ СОБЫТИЯ",
        "rec_col_n": "#",
        "rec_col_type": "Тип",
        "rec_col_detail": "Детали",
        "rec_col_delay": "Задержка мс",
        "rec_repeat_mode": "РЕЖИМ ПОВТОРА",
        "rec_repeat_inf": "БЕСКОНЕЧНО",
        "rec_repeat_count": "КОЛ-ВО РАЗ",
        "rec_repeat_timer": "ТАЙМЕР (сек)",
        "rec_repeats": "Повторений:",
        "rec_timer_sec": "Секунд:",
        "rec_recording": "● ЗАПИСЬ...",
        "rec_playing": "▶ ВОСПРОИЗВЕДЕНИЕ...",
        "rec_no_events": "Нет записанных событий!",
        "rec_events_count": "событий",
        # ---
        "set_lang": "ЯЗЫК",
        "set_topmost": "Поверх всех окон",
        "set_hotkey_start": "Горячая кл. СТАРТ/СТОП",
        "set_font": "ШРИФТ",
        "set_font_size": "Размер шрифта",
        "set_font_system": "Системные шрифты",
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
        "tab_record": "RECORD",
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
        "sc_delay": "Delay (ms)",
        "sc_loops": "Repeats (0=∞)",
        "sc_col_n": "#",
        "sc_col_x": "X",
        "sc_col_y": "Y",
        "sc_col_btn": "Button",
        "sc_col_type": "Type",
        "sc_col_delay": "Delay ms",
        # --- Record tab ---
        "rec_title": "ACTION RECORDER",
        "rec_desc": "Press F6 to start recording all actions (mouse, keyboard, scroll). Press F6 again to stop.",
        "rec_start": "⏺  START RECORDING",
        "rec_stop_rec": "⏹  STOP RECORDING",
        "rec_play": "▶  PLAY",
        "rec_stop_play": "■  STOP",
        "rec_clear": "🗑  CLEAR",
        "rec_events": "RECORDED EVENTS",
        "rec_col_n": "#",
        "rec_col_type": "Type",
        "rec_col_detail": "Details",
        "rec_col_delay": "Delay ms",
        "rec_repeat_mode": "REPEAT MODE",
        "rec_repeat_inf": "INFINITE",
        "rec_repeat_count": "COUNT",
        "rec_repeat_timer": "TIMER (sec)",
        "rec_repeats": "Repeats:",
        "rec_timer_sec": "Seconds:",
        "rec_recording": "● RECORDING...",
        "rec_playing": "▶ PLAYING...",
        "rec_no_events": "No recorded events!",
        "rec_events_count": "events",
        # ---
        "set_lang": "LANGUAGE",
        "set_topmost": "Always on top",
        "set_hotkey_start": "Hotkey START/STOP",
        "set_font": "FONT",
        "set_font_size": "Font size",
        "set_font_system": "System fonts",
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


# MacroEvent types: "click", "key_press", "key_release", "scroll", "move"
class MacroEvent:
    def __init__(self, kind, detail, delay_ms=0):
        self.kind = kind        # str
        self.detail = detail    # dict
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


# ── Main application ──────────────────────────────────────────────────────────
class FistClick:
    def __init__(self):
        self.cfg = load_config()
        self._lang = self.cfg.get("lang", "ru")
        self.spots = [ClickSpot() for _ in range(MAX_SPOTS)]
        self.script_steps = []
        self.running = False
        self.click_thread = None
        self.hotkey = self.cfg.get("hotkey", "f6")
        self.hotkey_listener = None
        self._mode = "spots"

        # Macro recorder state
        self._macro_events = []       # list[MacroEvent]
        self._macro_recording = False
        self._macro_playing = False
        self._macro_play_thread = None
        self._macro_kb_listener = None
        self._macro_ms_listener = None
        self._macro_last_time = None  # for timing between events

        # ── ВАЖНО: tk.Tk() ПЕРВЫМ, StringVar — только после него ─────────────
        self.root = tk.Tk()

        # Только здесь создаём StringVar — после Tk()
        self._follow_btn    = tk.StringVar(value="left")
        self._follow_type   = tk.StringVar(value="single")
        self._time_mode     = tk.StringVar(value="infinite")
        self._rec_rep_mode  = tk.StringVar(value="infinite")

        self.root.configure(bg=self.C("bg"))
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

    def _font(self, size=None, bold=False):
        fam = self.cfg.get("font_family", "Courier New")
        sz  = size or self.cfg.get("font_size", 9)
        w   = "bold" if bold else "normal"
        return (fam, sz, w)

    def _center(self):
        self.root.update_idletasks()
        w  = self.root.winfo_width()
        h  = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _sep(self, parent):
        tk.Frame(parent, bg=self.C("border"), height=1).pack(fill="x", padx=20, pady=8)

    def _radio(self, parent, text, var, val, cmd=None, bg_key="card", **kw):
        bg = self.C(bg_key)
        return tk.Radiobutton(parent, text=text, variable=var, value=val,
                              font=self._font(bold=True),
                              fg=self.C("text"), bg=bg,
                              selectcolor=self.C("accent"),
                              activebackground=bg,
                              relief="flat", bd=0, cursor="hand2",
                              indicatoron=0, padx=6, pady=2,
                              command=cmd, **kw)

    def _spin(self, parent, from_, to, label, default=0, bg_key="bg"):
        bg = self.C(bg_key)
        frame = tk.Frame(parent, bg=bg)
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
                 fg=self.C("text3"), bg=bg).pack()
        return var

    # ── build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        bg   = self.C("bg")
        root = self.root
        root.configure(bg=bg)

        # Title bar
        title_bar = tk.Frame(root, bg=bg, pady=14)
        title_bar.pack(fill="x", padx=20)
        tk.Label(title_bar, text="FIST",
                 font=self._font(22, True), fg=self.C("accent"), bg=bg).pack(side="left")
        tk.Label(title_bar, text=" CLICK",
                 font=self._font(22, True), fg=self.C("text"), bg=bg).pack(side="left")
        tk.Label(title_bar, text="  v2.0.2",
                 font=self._font(8), fg=self.C("text3"), bg=bg).pack(side="left", pady=(8, 0))

        self._status_dot = tk.Label(title_bar, text="\u25cf",
                                    font=self._font(13), fg=self.C("text3"), bg=bg)
        self._status_dot.pack(side="right", padx=(0, 4))
        self._status_lbl = tk.Label(title_bar, text=self.t("idle"),
                                    font=self._font(8, True), fg=self.C("text3"), bg=bg)
        self._status_lbl.pack(side="right")

        self._sep(root)

        # Tab bar
        tab_bar = tk.Frame(root, bg=bg)
        tab_bar.pack(fill="x", padx=20, pady=(0, 10))
        self._tab_btns = {}
        self._tabs = {}
        for key, lbl_key in [
            ("spots",    "tab_spots"),
            ("follow",   "tab_follow"),
            ("script",   "tab_script"),
            ("record",   "tab_record"),
            ("settings", "tab_settings"),
        ]:
            b = tk.Button(tab_bar, text=self.t(lbl_key),
                          font=self._font(8, True),
                          relief="flat", bd=0, padx=10, pady=6,
                          cursor="hand2",
                          command=lambda k=key: self._show_tab(k))
            b.pack(side="left", padx=(0, 2))
            self._tab_btns[key] = b

        # Content
        self._content = tk.Frame(root, bg=bg)
        self._content.pack(fill="both", expand=True)

        self._build_spots_tab()
        self._build_follow_tab()
        self._build_script_tab()
        self._build_record_tab()
        self._build_settings_tab()
        self._show_tab("spots")

        # Bottom controls
        self._sep(root)
        ctrl = tk.Frame(root, bg=bg)
        ctrl.pack(fill="x", padx=20, pady=(0, 6))

        self._start_btn = tk.Button(ctrl, text=self.t("start"),
                                    font=self._font(12, True),
                                    fg=self.C("bg"), bg=self.C("green"),
                                    activebackground="#25A244",
                                    activeforeground=self.C("bg"),
                                    relief="flat", bd=0, pady=11,
                                    cursor="hand2", command=self._start)
        self._start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

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
        self._counter_lbl = tk.Label(root, text=f"{self.t('clicks')}: 0",
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
                 ).pack(anchor="w", padx=20, pady=(4, 6))

        grid = tk.Frame(f, bg=bg)
        grid.pack(fill="x", padx=20)
        self._spot_cards = []
        for i, spot in enumerate(self.spots):
            card = self._make_spot_card(grid, i, spot)
            row, col = divmod(i, 2)
            card.grid(row=row, column=col,
                      padx=(0 if col == 0 else 5, 0),
                      pady=(0 if row == 0 else 5, 0),
                      sticky="nsew")
            self._spot_cards.append(card)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._sep(f)
        self._build_common_settings(f)

    def _make_spot_card(self, parent, index, spot):
        bg  = self.C("card")
        bdr = self.C("border")
        card = tk.Frame(parent, bg=bg, padx=10, pady=8,
                        highlightbackground=bdr, highlightthickness=1)

        hdr = tk.Frame(card, bg=bg)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text=f"{self.t('spot')} {index+1}",
                 font=self._font(8, True), fg=self.C("accent"), bg=bg).pack(side="left")

        en_var = tk.BooleanVar(value=spot.enabled)
        tk.Checkbutton(hdr, variable=en_var, text=self.t("on"),
                       font=self._font(7, True),
                       fg=self.C("green"), bg=bg, selectcolor=bg,
                       activebackground=bg, bd=0, relief="flat", cursor="hand2",
                       command=lambda: self._toggle_spot(spot, en_var)
                       ).pack(side="right")

        crow = tk.Frame(card, bg=bg)
        crow.pack(fill="x", pady=(0, 6))
        coord_lbl = tk.Label(crow, text="X: \u2014   Y: \u2014",
                             font=self._font(10, True),
                             fg=self.C("text"), bg=bg, width=14, anchor="w")
        coord_lbl.pack(side="left")
        tk.Button(crow, text=self.t("pick"),
                  font=self._font(7, True),
                  fg=self.C("bg"), bg=self.C("accent"),
                  activebackground=self.C("border"),
                  relief="flat", bd=0, padx=6, pady=2, cursor="hand2",
                  command=lambda s=spot, cl=coord_lbl: self._pick_spot(s, cl)
                  ).pack(side="right")

        opt = tk.Frame(card, bg=bg)
        opt.pack(fill="x")
        tk.Label(opt, text="BTN", font=self._font(7),
                 fg=self.C("text2"), bg=bg).pack(side="left")

        btn_var = tk.StringVar(value=spot.button)
        for val, lbl in [("left", self.t("btn_left")), ("right", self.t("btn_right"))]:
            self._radio(opt, lbl, btn_var, val,
                        cmd=lambda v=btn_var, s=spot: setattr(s, "button", v.get()),
                        bg_key="card"
                        ).pack(side="left", padx=(4, 0))

        tk.Label(opt, text="  \u00d7", font=self._font(7),
                 fg=self.C("text2"), bg=bg).pack(side="left", padx=(8, 0))

        type_var = tk.StringVar(value=spot.click_type)
        for val, lbl in [("single", self.t("type_single")), ("double", self.t("type_double"))]:
            self._radio(opt, lbl, type_var, val,
                        cmd=lambda v=type_var, s=spot: setattr(s, "click_type", v.get()),
                        bg_key="card"
                        ).pack(side="left", padx=(3, 0))

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
                 ).pack(anchor="w", padx=20, pady=(10, 4))
        tk.Label(f, text=self.t("follow_desc"),
                 font=self._font(8), fg=self.C("text2"), bg=bg,
                 wraplength=420, justify="left"
                 ).pack(anchor="w", padx=20, pady=(0, 12))

        card = tk.Frame(f, bg=self.C("card"),
                        highlightbackground=self.C("border"), highlightthickness=1)
        card.pack(fill="x", padx=20, pady=(0, 10))
        inner = tk.Frame(card, bg=self.C("card"), padx=12, pady=10)
        inner.pack(fill="x")

        row1 = tk.Frame(inner, bg=self.C("card"))
        row1.pack(fill="x", pady=(0, 6))
        tk.Label(row1, text=self.t("follow_btn"),
                 font=self._font(8, True), fg=self.C("text2"),
                 bg=self.C("card"), width=10, anchor="w").pack(side="left")
        for val, lbl in [("left", self.t("btn_left")), ("right", self.t("btn_right"))]:
            self._radio(row1, lbl, self._follow_btn, val, bg_key="card"
                        ).pack(side="left", padx=(4, 0))

        row2 = tk.Frame(inner, bg=self.C("card"))
        row2.pack(fill="x")
        tk.Label(row2, text=self.t("follow_type"),
                 font=self._font(8, True), fg=self.C("text2"),
                 bg=self.C("card"), width=10, anchor="w").pack(side="left")
        for val, lbl in [("single", self.t("type_single")), ("double", self.t("type_double"))]:
            self._radio(row2, lbl, self._follow_type, val, bg_key="card"
                        ).pack(side="left", padx=(4, 0))

        self._sep(f)
        self._build_common_settings(f)

    # ── SCRIPT TAB ────────────────────────────────────────────────────────────
    def _build_script_tab(self):
        bg = self.C("bg")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["script"] = f

        tk.Label(f, text=self.t("script_title"),
                 font=self._font(10, True), fg=self.C("accent"), bg=bg
                 ).pack(anchor="w", padx=20, pady=(10, 4))
        tk.Label(f, text=self.t("script_desc"),
                 font=self._font(8), fg=self.C("text2"), bg=bg,
                 wraplength=420, justify="left"
                 ).pack(anchor="w", padx=20, pady=(0, 8))

        tb = tk.Frame(f, bg=bg)
        tb.pack(fill="x", padx=20, pady=(0, 6))
        for key, cmd in [("sc_add", self._sc_add), ("sc_del", self._sc_del),
                         ("sc_up", self._sc_up), ("sc_dn", self._sc_dn)]:
            tk.Button(tb, text=self.t(key),
                      font=self._font(8, True),
                      fg=self.C("text"), bg=self.C("card"),
                      activebackground=self.C("border"),
                      relief="flat", bd=0, padx=10, pady=4,
                      cursor="hand2", command=cmd
                      ).pack(side="left", padx=(0, 4))

        tbl_frame = tk.Frame(f, bg=self.C("card"),
                             highlightbackground=self.C("border"), highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        cols     = ("n", "x", "y", "btn", "type", "delay")
        col_keys = ("sc_col_n", "sc_col_x", "sc_col_y",
                    "sc_col_btn", "sc_col_type", "sc_col_delay")
        col_w    = (30, 60, 60, 70, 60, 80)

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

        sb_tree = ttk.Scrollbar(tbl_frame, orient="vertical",
                                command=self._sc_tree.yview)
        self._sc_tree.configure(yscrollcommand=sb_tree.set)
        sb_tree.pack(side="right", fill="y")
        self._sc_tree.pack(fill="both", expand=True)

        lp_row = tk.Frame(f, bg=bg)
        lp_row.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(lp_row, text=self.t("sc_loops"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0, 8))
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
                i + 1, s.x, s.y, s.button, s.click_type, s.delay_ms
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
        if i is not None and i < len(self.script_steps) - 1:
            self.script_steps[i], self.script_steps[i+1] = \
                self.script_steps[i+1], self.script_steps[i]
            self._sc_refresh()
            self._sc_tree.selection_set(self._sc_tree.get_children()[i+1])

    # ── RECORD TAB ────────────────────────────────────────────────────────────
    def _build_record_tab(self):
        bg  = self.C("bg")
        card_bg = self.C("card")
        f = tk.Frame(self._content, bg=bg)
        self._tabs["record"] = f

        # Title + description
        tk.Label(f, text=self.t("rec_title"),
                 font=self._font(10, True), fg=self.C("accent"), bg=bg
                 ).pack(anchor="w", padx=20, pady=(10, 2))
        tk.Label(f, text=self.t("rec_desc"),
                 font=self._font(8), fg=self.C("text2"), bg=bg,
                 wraplength=440, justify="left"
                 ).pack(anchor="w", padx=20, pady=(0, 8))

        # Control buttons row
        btns = tk.Frame(f, bg=bg)
        btns.pack(fill="x", padx=20, pady=(0, 8))

        self._rec_start_btn = tk.Button(
            btns, text=self.t("rec_start"),
            font=self._font(8, True),
            fg=self.C("bg"), bg=self.C("accent"),
            activebackground="#CC2D24", activeforeground=self.C("bg"),
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
            command=self._rec_start_recording
        )
        self._rec_start_btn.pack(side="left", padx=(0, 4))

        self._rec_stop_rec_btn = tk.Button(
            btns, text=self.t("rec_stop_rec"),
            font=self._font(8, True),
            fg=self.C("text"), bg=self.C("card"),
            activebackground=self.C("border"),
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
            state="disabled",
            command=self._rec_stop_recording
        )
        self._rec_stop_rec_btn.pack(side="left", padx=(0, 4))

        self._rec_play_btn = tk.Button(
            btns, text=self.t("rec_play"),
            font=self._font(8, True),
            fg=self.C("bg"), bg=self.C("green"),
            activebackground="#25A244", activeforeground=self.C("bg"),
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
            command=self._rec_play
        )
        self._rec_play_btn.pack(side="left", padx=(0, 4))

        self._rec_stop_play_btn = tk.Button(
            btns, text=self.t("rec_stop_play"),
            font=self._font(8, True),
            fg=self.C("text"), bg=self.C("card"),
            activebackground=self.C("border"),
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
            state="disabled",
            command=self._rec_stop_play
        )
        self._rec_stop_play_btn.pack(side="left", padx=(0, 4))

        tk.Button(
            btns, text=self.t("rec_clear"),
            font=self._font(8, True),
            fg=self.C("text2"), bg=self.C("card"),
            activebackground=self.C("border"),
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
            command=self._rec_clear
        ).pack(side="left", padx=(0, 4))

        # Status label for recording/playing
        self._rec_status_lbl = tk.Label(
            btns, text="",
            font=self._font(8, True), fg=self.C("accent"), bg=bg
        )
        self._rec_status_lbl.pack(side="right", padx=(8, 0))

        # Events count label
        self._rec_count_lbl = tk.Label(
            f, text=f"0 {self.t('rec_events_count')}",
            font=self._font(7), fg=self.C("text3"), bg=bg
        )
        self._rec_count_lbl.pack(anchor="w", padx=20, pady=(0, 4))

        # Treeview for events
        tbl_frame = tk.Frame(f, bg=card_bg,
                             highlightbackground=self.C("border"), highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        rec_cols     = ("n", "type", "detail", "delay")
        rec_col_keys = ("rec_col_n", "rec_col_type", "rec_col_detail", "rec_col_delay")
        rec_col_w    = (30, 90, 220, 80)

        style = ttk.Style()
        style.configure("Record.Treeview",
                        background=card_bg,
                        foreground=self.C("text"),
                        fieldbackground=card_bg,
                        rowheight=22,
                        font=self._font())
        style.configure("Record.Treeview.Heading",
                        background=self.C("border"),
                        foreground=self.C("text2"),
                        font=self._font(bold=True))
        style.map("Record.Treeview",
                  background=[("selected", self.C("accent"))],
                  foreground=[("selected", "white")])

        self._rec_tree = ttk.Treeview(tbl_frame, columns=rec_cols, show="headings",
                                      height=7, style="Record.Treeview")
        for c, k, w in zip(rec_cols, rec_col_keys, rec_col_w):
            self._rec_tree.heading(c, text=self.t(k))
            self._rec_tree.column(c, width=w, anchor="center" if w < 100 else "w")

        rec_sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self._rec_tree.yview)
        self._rec_tree.configure(yscrollcommand=rec_sb.set)
        rec_sb.pack(side="right", fill="y")
        self._rec_tree.pack(fill="both", expand=True)

        # ── Repeat mode ──────────────────────────────────────────────────────
        self._sep(f)
        rep_hdr = tk.Frame(f, bg=bg)
        rep_hdr.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(rep_hdr, text=self.t("rec_repeat_mode"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg
                 ).pack(side="left")

        rep_row = tk.Frame(f, bg=bg)
        rep_row.pack(fill="x", padx=20, pady=(0, 4))

        for val, key in [
            ("infinite", "rec_repeat_inf"),
            ("count",    "rec_repeat_count"),
            ("timer",    "rec_repeat_timer"),
        ]:
            tk.Radiobutton(
                rep_row, text=self.t(key),
                variable=self._rec_rep_mode, value=val,
                font=self._font(bold=True),
                fg=self.C("text"), bg=bg, selectcolor=bg,
                activebackground=bg, relief="flat", bd=0,
                cursor="hand2", indicatoron=0, padx=8, pady=3,
                command=self._rec_update_rep_widgets
            ).pack(side="left", padx=(0, 4))

        rep_params = tk.Frame(f, bg=bg)
        rep_params.pack(fill="x", padx=20, pady=(2, 10))

        # count widget
        self._rec_rep_count_frame = tk.Frame(rep_params, bg=bg)
        tk.Label(self._rec_rep_count_frame, text=self.t("rec_repeats"),
                 font=self._font(8), fg=self.C("text2"), bg=bg).pack(side="left", padx=(0, 6))
        self._rec_rep_count_var = tk.StringVar(value="5")
        tk.Spinbox(self._rec_rep_count_frame, from_=1, to=9999,
                   textvariable=self._rec_rep_count_var,
                   width=6, font=self._font(),
                   fg=self.C("text"), bg=self.C("card"),
                   insertbackground=self.C("text"),
                   relief="flat", bd=1,
                   highlightbackground=self.C("border"), highlightthickness=1
                   ).pack(side="left")

        # timer widget
        self._rec_rep_timer_frame = tk.Frame(rep_params, bg=bg)
        tk.Label(self._rec_rep_timer_frame, text=self.t("rec_timer_sec"),
                 font=self._font(8), fg=self.C("text2"), bg=bg).pack(side="left", padx=(0, 6))
        self._rec_rep_timer_var = tk.StringVar(value="30")
        tk.Spinbox(self._rec_rep_timer_frame, from_=1, to=86400,
                   textvariable=self._rec_rep_timer_var,
                   width=7, font=self._font(),
                   fg=self.C("text"), bg=self.C("card"),
                   insertbackground=self.C("text"),
                   relief="flat", bd=1,
                   highlightbackground=self.C("border"), highlightthickness=1
                   ).pack(side="left")

        self._rec_update_rep_widgets()

    def _rec_update_rep_widgets(self):
        self._rec_rep_count_frame.pack_forget()
        self._rec_rep_timer_frame.pack_forget()
        mode = self._rec_rep_mode.get()
        if mode == "count":
            self._rec_rep_count_frame.pack(side="left")
        elif mode == "timer":
            self._rec_rep_timer_frame.pack(side="left")

    def _rec_refresh_tree(self):
        self._rec_tree.delete(*self._rec_tree.get_children())
        for i, ev in enumerate(self._macro_events):
            detail = self._ev_detail_str(ev)
            self._rec_tree.insert("", "end", values=(i+1, ev.kind, detail, ev.delay_ms))
        self._rec_count_lbl.config(
            text=f"{len(self._macro_events)} {self.t('rec_events_count')}"
        )
        # Auto scroll to bottom
        if self._rec_tree.get_children():
            self._rec_tree.see(self._rec_tree.get_children()[-1])

    @staticmethod
    def _ev_detail_str(ev):
        d = ev.detail
        k = ev.kind
        if k == "click":
            return f"{d.get('button','?')} ({d.get('x',0)},{d.get('y',0)}) {'press' if d.get('pressed') else 'release'}"
        elif k == "key_press":
            return f"press: {d.get('key','?')}"
        elif k == "key_release":
            return f"release: {d.get('key','?')}"
        elif k == "scroll":
            return f"scroll ({d.get('x',0)},{d.get('y',0)}) dx={d.get('dx',0)} dy={d.get('dy',0)}"
        elif k == "move":
            return f"move ({d.get('x',0)},{d.get('y',0)})"
        return str(d)

    # ── Recording logic ───────────────────────────────────────────────────────
    def _rec_start_recording(self):
        if not PYNPUT_OK:
            self._flash(self.t("no_pyautogui"))
            return
        if self._macro_recording:
            return
        self._macro_events.clear()
        self._macro_last_time = time.time()
        self._macro_recording = True

        self._rec_start_btn.config(state="disabled")
        self._rec_stop_rec_btn.config(state="normal")
        self._rec_play_btn.config(state="disabled")
        self._rec_status_lbl.config(text=self.t("rec_recording"), fg=self.C("accent"))
        self._rec_refresh_tree()

        # Start pynput listeners
        self._macro_kb_listener = pynkeyboard.Listener(
            on_press=self._rec_on_key_press,
            on_release=self._rec_on_key_release
        )
        self._macro_ms_listener = pynmouse.Listener(
            on_click=self._rec_on_click,
            on_scroll=self._rec_on_scroll
            # on_move excluded intentionally to avoid event flood
        )
        self._macro_kb_listener.daemon = True
        self._macro_ms_listener.daemon = True
        self._macro_kb_listener.start()
        self._macro_ms_listener.start()

    def _rec_stop_recording(self):
        self._macro_recording = False
        if self._macro_kb_listener:
            try:
                self._macro_kb_listener.stop()
            except Exception:
                pass
            self._macro_kb_listener = None
        if self._macro_ms_listener:
            try:
                self._macro_ms_listener.stop()
            except Exception:
                pass
            self._macro_ms_listener = None

        self._rec_start_btn.config(state="normal")
        self._rec_stop_rec_btn.config(state="disabled")
        self._rec_play_btn.config(state="normal")
        self._rec_status_lbl.config(text="")
        self.root.after(0, self._rec_refresh_tree)

    def _rec_record_event(self, kind, detail):
        if not self._macro_recording:
            return
        now = time.time()
        delay_ms = int((now - self._macro_last_time) * 1000)
        self._macro_last_time = now
        ev = MacroEvent(kind, detail, delay_ms)
        self._macro_events.append(ev)
        # Update UI from main thread every 5 events
        if len(self._macro_events) % 5 == 0:
            self.root.after(0, self._rec_refresh_tree)

    def _rec_on_key_press(self, key):
        # Skip F6 to avoid recording the hotkey itself
        try:
            name = key.name if hasattr(key, "name") else str(key)
        except Exception:
            name = str(key)
        if name and name.lower() == self.hotkey:
            return
        self._rec_record_event("key_press", {"key": name})

    def _rec_on_key_release(self, key):
        try:
            name = key.name if hasattr(key, "name") else str(key)
        except Exception:
            name = str(key)
        if name and name.lower() == self.hotkey:
            return
        self._rec_record_event("key_release", {"key": name})

    def _rec_on_click(self, x, y, button, pressed):
        btn_name = button.name if hasattr(button, "name") else str(button)
        self._rec_record_event("click", {"x": x, "y": y, "button": btn_name, "pressed": pressed})

    def _rec_on_scroll(self, x, y, dx, dy):
        self._rec_record_event("scroll", {"x": x, "y": y, "dx": dx, "dy": dy})

    # ── Playback logic ────────────────────────────────────────────────────────
    def _rec_play(self):
        if not PYAUTOGUI_OK or not PYNPUT_OK:
            self._flash(self.t("no_pyautogui"))
            return
        if not self._macro_events:
            self._flash(self.t("rec_no_events"))
            return
        if self._macro_playing or self._macro_recording:
            return

        self._macro_playing = True
        self._rec_play_btn.config(state="disabled")
        self._rec_stop_play_btn.config(state="normal")
        self._rec_start_btn.config(state="disabled")
        self._rec_status_lbl.config(text=self.t("rec_playing"), fg=self.C("green"))

        self._macro_play_thread = threading.Thread(
            target=self._rec_play_loop, daemon=True
        )
        self._macro_play_thread.start()

    def _rec_stop_play(self):
        self._macro_playing = False

    def _rec_play_loop(self):
        mode = self._rec_rep_mode.get()
        try:
            count = int(self._rec_rep_count_var.get())
        except Exception:
            count = 1
        try:
            timer_sec = float(self._rec_rep_timer_var.get())
        except Exception:
            timer_sec = 30.0

        end_time = (time.time() + timer_sec) if mode == "timer" else None
        iteration = 0

        # Use pynput controller for keyboard
        kb_ctrl = pynkeyboard.Controller()
        ms_ctrl = pynmouse.Controller()

        while self._macro_playing:
            if mode == "timer" and time.time() >= end_time:
                break
            if mode == "count" and iteration >= count:
                break

            for ev in self._macro_events:
                if not self._macro_playing:
                    break
                # Respect original timing
                delay_s = ev.delay_ms / 1000.0
                if delay_s > 0:
                    slept = 0.0
                    step = 0.02
                    while slept < delay_s and self._macro_playing:
                        time.sleep(min(step, delay_s - slept))
                        slept += step
                if not self._macro_playing:
                    break
                try:
                    self._rec_play_event(ev, kb_ctrl, ms_ctrl)
                except Exception:
                    pass

            iteration += 1

        self.root.after(0, self._rec_play_done)

    def _rec_play_event(self, ev, kb_ctrl, ms_ctrl):
        d = ev.detail
        if ev.kind == "click":
            x, y = d.get("x", 0), d.get("y", 0)
            btn_name = d.get("button", "left")
            pressed  = d.get("pressed", True)
            # Map name to pynput button
            btn_map = {
                "left":   pynmouse.Button.left,
                "right":  pynmouse.Button.right,
                "middle": pynmouse.Button.middle,
            }
            btn = btn_map.get(btn_name, pynmouse.Button.left)
            ms_ctrl.position = (x, y)
            if pressed:
                ms_ctrl.press(btn)
            else:
                ms_ctrl.release(btn)

        elif ev.kind == "scroll":
            x, y   = d.get("x", 0), d.get("y", 0)
            dx, dy = d.get("dx", 0), d.get("dy", 0)
            ms_ctrl.position = (x, y)
            ms_ctrl.scroll(dx, dy)

        elif ev.kind == "key_press":
            key_name = d.get("key", "")
            self._kb_press(kb_ctrl, key_name)

        elif ev.kind == "key_release":
            key_name = d.get("key", "")
            self._kb_release(kb_ctrl, key_name)

    @staticmethod
    def _kb_press(ctrl, key_name):
        try:
            special = getattr(pynkeyboard.Key, key_name, None)
            if special:
                ctrl.press(special)
            else:
                ctrl.press(key_name)
        except Exception:
            pass

    @staticmethod
    def _kb_release(ctrl, key_name):
        try:
            special = getattr(pynkeyboard.Key, key_name, None)
            if special:
                ctrl.release(special)
            else:
                ctrl.release(key_name)
        except Exception:
            pass

    def _rec_play_done(self):
        self._macro_playing = False
        self._rec_play_btn.config(state="normal")
        self._rec_stop_play_btn.config(state="disabled")
        self._rec_start_btn.config(state="normal")
        self._rec_status_lbl.config(text="")

    def _rec_clear(self):
        self._macro_events.clear()
        self._rec_refresh_tree()

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
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<MouseWheel>",
                   lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        p = inner

        def sec(key):
            tk.Label(p, text=self.t(key),
                     font=self._font(8, True), fg=self.C("text2"), bg=bg
                     ).pack(anchor="w", padx=20, pady=(12, 4))

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
                           ).pack(side="left", padx=(0, 12))

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
        self._hk_lbl = tk.Label(hkr,
                                 text=(self.hotkey.upper() if self.hotkey else "\u2014"),
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
        self._hk_set_btn.pack(side="left", padx=(6, 0))
        tk.Button(hkr, text=self.t("clear"),
                  font=self._font(bold=True),
                  fg=self.C("text2"), bg=self.C("card"),
                  activebackground=self.C("border"),
                  relief="flat", bd=0, padx=8, pady=3,
                  cursor="hand2", command=self._clear_hotkey
                  ).pack(side="left", padx=(4, 0))

        # Font
        sec("set_font")
        fr = row()
        tk.Label(fr, text=self.t("set_font_size"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0, 6))
        self._font_size_var = tk.StringVar(value=str(self.cfg.get("font_size", 9)))
        tk.Spinbox(fr, from_=7, to=16, textvariable=self._font_size_var,
                   width=4, font=self._font(),
                   fg=self.C("text"), bg=self.C("card"),
                   insertbackground=self.C("text"),
                   relief="flat", bd=1,
                   highlightbackground=self.C("border"), highlightthickness=1
                   ).pack(side="left")

        fr2 = row()
        tk.Label(fr2, text=self.t("set_font_system"),
                 font=self._font(8), fg=self.C("text2"), bg=bg
                 ).pack(side="left", padx=(0, 6))
        avail = sorted(tkfont.families())
        self._font_fam_var = tk.StringVar(value=self.cfg.get("font_family", "Courier New"))
        ttk.Combobox(fr2, textvariable=self._font_fam_var,
                     values=avail, width=22, state="readonly").pack(side="left")

        # Theme
        sec("set_theme")
        for cfg_key, lbl_key in [("bg", "set_bg"), ("accent", "set_accent")]:
            cr = row()
            tk.Label(cr, text=self.t(lbl_key),
                     font=self._font(8), fg=self.C("text2"), bg=bg,
                     width=16, anchor="w").pack(side="left")
            cur_color = self.cfg.get(cfg_key, DEFAULT_CFG[cfg_key])
            swatch = tk.Label(cr, bg=cur_color, width=4, relief="flat", cursor="hand2")
            swatch.pack(side="left", padx=(0, 6), ipady=8)
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
                  ).pack(side="left", padx=(0, 8))
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
        self._hk_lbl.config(text="\u2014", fg=self.C("text3"))
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None

    def _save_settings(self):
        self.cfg["lang"]        = self._lang_var.get()
        self.cfg["topmost"]     = self._topmost_var.get()
        self.cfg["hotkey"]      = self.hotkey
        try:
            self.cfg["font_size"] = int(self._font_size_var.get())
        except Exception:
            pass
        self.cfg["font_family"] = self._font_fam_var.get()
        save_config(self.cfg)
        self.root.attributes("-topmost", self.cfg["topmost"])
        self._start_hk_listener()
        messagebox.showinfo("FIST CLICK", self.t("saved"))

    def _reset_settings(self):
        self.cfg = dict(DEFAULT_CFG)
        save_config(self.cfg)
        messagebox.showinfo("FIST CLICK", self.t("saved"))

    # ── Common settings ───────────────────────────────────────────────────────
    def _build_common_settings(self, parent):
        bg = self.C("bg")

        ivl = tk.Frame(parent, bg=bg)
        ivl.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(ivl, text=self.t("interval"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        self._ivl_h  = self._spin(ivl, 0, 23, "h")
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg, font=self._font(11)).pack(side="left")
        self._ivl_m  = self._spin(ivl, 0, 59, "m")
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg, font=self._font(11)).pack(side="left")
        self._ivl_s  = self._spin(ivl, 0, 59, "s", default=1)
        tk.Label(ivl, text=":", fg=self.C("text2"), bg=bg, font=self._font(11)).pack(side="left")
        self._ivl_ms = self._spin(ivl, 0, 999, "ms")

        dur = tk.Frame(parent, bg=bg)
        dur.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(dur, text=self.t("duration"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        for val, key in [("infinite", "infinite"), ("timer", "timer")]:
            tk.Radiobutton(dur, text=self.t(key), variable=self._time_mode, value=val,
                           font=self._font(bold=True),
                           fg=self.C("text"), bg=bg, selectcolor=bg,
                           activebackground=bg, relief="flat", bd=0,
                           cursor="hand2", indicatoron=0, padx=8, pady=3
                           ).pack(side="left", padx=(0, 4))

        tmr = tk.Frame(parent, bg=bg)
        tmr.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(tmr, text=self.t("timer_dur"),
                 font=self._font(8, True), fg=self.C("text2"), bg=bg,
                 width=14, anchor="w").pack(side="left")
        self._tmr_h = self._spin(tmr, 0, 23, "h")
        tk.Label(tmr, text=":", fg=self.C("text2"), bg=bg, font=self._font(11)).pack(side="left")
        self._tmr_m = self._spin(tmr, 0, 59, "m")
        tk.Label(tmr, text=":", fg=self.C("text2"), bg=bg, font=self._font(11)).pack(side="left")
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

    # ── Start / Stop (clicker) ────────────────────────────────────────────────
    def _toggle(self):
        # If record tab is active — toggle recording instead
        if self._mode == "record":
            if self._macro_recording:
                self._rec_stop_recording()
            elif not self._macro_playing:
                self._rec_start_recording()
            return
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
        elif self._mode == "record":
            # Handled via _toggle
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
        self._counter_lbl.config(text=f"{self.t('clicks')}: {self._click_count:,}")

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
        active   = [s for s in self.spots if s.enabled and s.x is not None]
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
        btn = self._follow_btn.get() or "left"
        typ = self._follow_type.get() or "single"
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
        infinite  = (loops == 0)
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
        self._macro_playing = False
        self._macro_recording = False
        for listener in [self.hotkey_listener, self._macro_kb_listener, self._macro_ms_listener]:
            if listener:
                try:
                    listener.stop()
                except Exception:
                    pass
        self.root.destroy()


if __name__ == "__main__":
    FistClick()
