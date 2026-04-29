# -*- coding: utf-8 -*-
"""
FIST CLICK — Установщик v2.0.0
Автоматически: проверяет Python, скачивает, ставит зависимости, собирает EXE.
Автодобавление FIST-CLICK к любому выбранному пути.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import os
import zipfile
import shutil
import urllib.request
import winreg

REPO_OWNER = "Achinsky"
REPO_NAME  = "FIST-CLICK"
GITHUB_ZIP = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/main.zip"
APP_FOLDER = "FIST-CLICK"   # always appended

C = {
    "bg":     "#181A20",
    "card":   "#22252E",
    "border": "#313540",
    "accent": "#FF3B30",
    "green":  "#30D158",
    "text":   "#EAEAEA",
    "text2":  "#8A8A8E",
    "text3":  "#48484A",
    "bar_bg": "#2C2C2E",
}


# ─────────────────────────────────────────────────────────────────────────────
def find_python():
    for cmd in ("py", "python", "python3"):
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and "Python 3" in r.stdout + r.stderr:
                return cmd
        except Exception:
            pass
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for sub in (r"SOFTWARE\Python\PythonCore",
                    r"SOFTWARE\WOW6432Node\Python\PythonCore"):
            try:
                with winreg.OpenKey(hive, sub) as key:
                    i = 0
                    while True:
                        try:
                            ver = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, rf"{ver}\InstallPath") as ip:
                                path = winreg.QueryValueEx(ip, "ExecutablePath")[0]
                                if os.path.exists(path):
                                    return path
                        except OSError:
                            break
                        i += 1
            except Exception:
                pass
    return None


def pip_install(python, packages):
    r = subprocess.run(
        [python, "-m", "pip", "install", "--upgrade", *packages],
        capture_output=True, text=True, timeout=300,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if r.returncode != 0:
        raise RuntimeError(f"pip error:\n{r.stderr[-500:]}")


# ─────────────────────────────────────────────────────────────────────────────
class ProgressBar(tk.Canvas):
    def __init__(self, parent, **kw):
        bg = kw.pop("bg", C["bar_bg"])
        super().__init__(parent, height=5, bg=bg, highlightthickness=0, **kw)
        self._pct = 0.0
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, pct):
        self._pct = max(0.0, min(1.0, pct))
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        f = int(w * self._pct)
        for x in range(f):
            t = x / max(w, 1)
            r = int(0xFF*(1-t)+0x30*t)
            g = int(0x3B*(1-t)+0xD1*t)
            b = int(0x30*(1-t)+0x58*t)
            self.create_line(x, 0, x, 5, fill=f"#{r:02x}{g:02x}{b:02x}")


class LogBox(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1, **kw)
        self._t = tk.Text(self, height=7, font=("Courier New", 8),
                          fg=C["text2"], bg=C["card"], relief="flat", bd=0,
                          state="disabled", wrap="char",
                          insertbackground=C["text"])
        sb = tk.Scrollbar(self, command=self._t.yview,
                          bg=C["border"], troughcolor=C["card"],
                          activebackground=C["text3"],
                          relief="flat", bd=0, width=8)
        self._t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._t.pack(side="left", fill="both", expand=True, padx=6, pady=4)

    def append(self, line):
        def _do():
            self._t.configure(state="normal")
            self._t.insert("end", line + "\n")
            self._t.see("end")
            self._t.configure(state="disabled")
        try:
            self._t.after(0, _do)
        except Exception:
            pass

    def clear(self):
        self._t.configure(state="normal")
        self._t.delete("1.0", "end")
        self._t.configure(state="disabled")

    def get_all(self):
        return self._t.get("1.0", "end")


# ─────────────────────────────────────────────────────────────────────────────
class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FIST CLICK — Установщик v2.0")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self._center(530, 720)
        self._build()
        self.root.mainloop()

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _clip(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        if btn:
            orig = btn.cget("text")
            btn.config(text="✓ Скопировано", fg=C["green"])
            self.root.after(1500, lambda: btn.config(text=orig, fg=C["text2"]))

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        r = self.root
        bg = C["bg"]

        # Header
        hdr = tk.Frame(r, bg=bg, pady=18)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text="FIST", font=("Courier New", 24, "bold"),
                 fg=C["accent"], bg=bg).pack(side="left")
        tk.Label(hdr, text=" CLICK", font=("Courier New", 24, "bold"),
                 fg=C["text"], bg=bg).pack(side="left")
        tk.Label(hdr, text="  УСТАНОВЩИК  v2.0", font=("Courier New", 9),
                 fg=C["text2"], bg=bg).pack(side="left", pady=(6,0))
        tk.Frame(r, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0,16))

        # Install path
        tk.Label(r, text="ПАПКА УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=bg
                 ).pack(anchor="w", padx=24)

        # Default = home/FIST-CLICK
        default_path = os.path.join(os.path.expanduser("~"), APP_FOLDER)
        self._path_var = tk.StringVar(value=default_path)

        path_row = tk.Frame(r, bg=bg)
        path_row.pack(fill="x", padx=24, pady=(5,4))
        self._path_entry = tk.Entry(
            path_row, textvariable=self._path_var,
            font=("Courier New", 10), fg=C["text"], bg=C["card"],
            insertbackground=C["text"], relief="flat", bd=0,
            highlightbackground=C["border"], highlightthickness=1,
        )
        self._path_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0,5))

        self._cp_btn = tk.Button(
            path_row, text="⊙",
            font=("Courier New", 11), fg=C["text2"], bg=C["card"],
            activebackground=C["border"], relief="flat", bd=0,
            padx=8, pady=5, cursor="hand2",
            command=lambda: self._clip(self._path_var.get(), self._cp_btn),
        )
        self._cp_btn.pack(side="left", padx=(0,5))

        tk.Button(
            path_row, text="📁",
            font=("Courier New", 11), fg=C["text"], bg=C["card"],
            activebackground=C["border"], relief="flat", bd=0,
            padx=10, pady=5, cursor="hand2", command=self._browse,
        ).pack(side="left")

        # Hint: FIST-CLICK always appended
        tk.Label(r, text=f'  Папка «{APP_FOLDER}» добавляется автоматически',
                 font=("Courier New", 7), fg=C["text3"], bg=bg
                 ).pack(anchor="w", padx=24, pady=(0,10))

        # Options
        self._shortcut_var  = tk.BooleanVar(value=True)
        self._startmenu_var = tk.BooleanVar(value=True)
        opts = tk.Frame(r, bg=bg)
        opts.pack(fill="x", padx=24, pady=(0,14))
        for var, text in [
            (self._shortcut_var,  "Создать ярлык на рабочем столе"),
            (self._startmenu_var, "Добавить в меню Пуск"),
        ]:
            row = tk.Frame(opts, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Checkbutton(row, variable=var, text=text,
                           font=("Courier New", 9), fg=C["text"], bg=bg,
                           selectcolor=bg, activebackground=bg,
                           relief="flat", bd=0, cursor="hand2",
                           ).pack(side="left")

        tk.Frame(r, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0,14))

        # Steps
        tk.Label(r, text="ЭТАПЫ УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=bg
                 ).pack(anchor="w", padx=24)
        self._step_labels = []
        sf = tk.Frame(r, bg=bg)
        sf.pack(fill="x", padx=24, pady=(6,12))
        for text in [
            "Проверка Python",
            "Скачивание FIST CLICK с GitHub",
            "Установка зависимостей",
            "Сборка FIST_CLICK.exe",
            "Создание ярлыков",
        ]:
            row = tk.Frame(sf, bg=bg)
            row.pack(fill="x", pady=2)
            dot = tk.Label(row, text="○", font=("Courier New", 11),
                           fg=C["text3"], bg=bg, width=2)
            dot.pack(side="left")
            lbl = tk.Label(row, text=text, font=("Courier New", 9),
                           fg=C["text3"], bg=bg, anchor="w")
            lbl.pack(side="left")
            self._step_labels.append((dot, lbl))

        # Progress
        self._progress = ProgressBar(r, bg=C["bar_bg"])
        self._progress.pack(fill="x", padx=24, pady=(0,4))
        self._prog_lbl = tk.Label(r, text="Готов к установке",
                                  font=("Courier New", 8),
                                  fg=C["text2"], bg=bg)
        self._prog_lbl.pack(anchor="w", padx=24, pady=(0,10))

        # Log
        log_hdr = tk.Frame(r, bg=bg)
        log_hdr.pack(fill="x", padx=24, pady=(0,4))
        tk.Label(log_hdr, text="ЛОГ УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=bg
                 ).pack(side="left")
        tk.Label(log_hdr, text="(прогресс сборки в реальном времени)",
                 font=("Courier New", 7), fg=C["text3"], bg=bg
                 ).pack(side="left", padx=(8,0))
        self._cl_btn = tk.Button(
            log_hdr, text="⊙ Копировать лог",
            font=("Courier New", 7), fg=C["text2"], bg=bg,
            activebackground=bg, activeforeground=C["green"],
            relief="flat", bd=0, padx=4, pady=0,
            cursor="hand2",
            command=lambda: self._clip(self._logbox.get_all(), self._cl_btn),
        )
        self._cl_btn.pack(side="right")

        self._logbox = LogBox(r)
        self._logbox.pack(fill="x", padx=24, pady=(0,14))

        tk.Frame(r, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0,14))

        self._install_btn = tk.Button(
            r, text="▶  УСТАНОВИТЬ",
            font=("Courier New", 13, "bold"),
            fg=C["bg"], bg=C["green"],
            activebackground="#25A244", activeforeground=C["bg"],
            relief="flat", bd=0, pady=13,
            cursor="hand2", command=self._start,
        )
        self._install_btn.pack(fill="x", padx=24, pady=(0,20))

    # ── Browse — автодобавление FIST-CLICK ────────────────────────────────────
    def _browse(self):
        """Открыть диалог выбора папки. Автоматически добавляет /FIST-CLICK."""
        base = filedialog.askdirectory(title="Выберите папку для установки")
        if base:
            # Если пользователь уже выбрал папку FIST-CLICK — не дублировать
            if os.path.basename(base) == APP_FOLDER:
                self._path_var.set(base)
            else:
                self._path_var.set(os.path.join(base, APP_FOLDER))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _set_step(self, i, state):
        dot, lbl = self._step_labels[i]
        cfg = {
            "wait":   ("○", C["text3"], C["text3"]),
            "active": ("◉", C["accent"], C["text"]),
            "done":   ("✓", C["green"],  C["text"]),
            "error":  ("✗", C["accent"], C["accent"]),
        }[state]
        dot.config(text=cfg[0], fg=cfg[1])
        lbl.config(fg=cfg[2])

    def _ui(self, fn):
        self.root.after(0, fn)

    def _log(self, msg, pct=None):
        def _do():
            self._prog_lbl.config(text=msg)
            if pct is not None:
                self._progress.set(pct)
        self._ui(_do)

    def _mark(self, i, state):
        self._ui(lambda: self._set_step(i, state))

    def _ll(self, line):
        self._logbox.append(line)

    # ── Install ───────────────────────────────────────────────────────────────
    def _start(self):
        self._install_btn.config(state="disabled", text="Установка…")
        self._logbox.clear()
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        # Ensure FIST-CLICK is always last segment
        raw = self._path_var.get().strip()
        if os.path.basename(raw) != APP_FOLDER:
            install_dir = os.path.join(raw, APP_FOLDER)
            self._ui(lambda: self._path_var.set(install_dir))
        else:
            install_dir = raw
        try:
            self._install(install_dir)
        except Exception as e:
            self._ui(lambda: self._on_error(str(e)))

    def _install(self, install_dir):
        os.makedirs(install_dir, exist_ok=True)
        tmp = os.path.join(install_dir, "_tmp")
        os.makedirs(tmp, exist_ok=True)

        # Step 0: Python
        self._mark(0, "active")
        self._log("Поиск Python...", 0.02)
        self._ll(">> Поиск Python...")
        python = find_python()
        if python is None:
            self._ll(">> Скачиваем Python 3.12...")
            py_exe = os.path.join(tmp, "python_setup.exe")
            urllib.request.urlretrieve(
                "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
                py_exe,
                reporthook=lambda b, bs, ts: self._log(
                    f"Python: {min(b*bs,ts)//1024}/{ts//1024} КБ",
                    0.05 + 0.1*(b*bs/max(ts,1))
                )
            )
            subprocess.run(
                [py_exe, "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1"],
                check=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0,
            )
            python = find_python()
            if python is None:
                raise RuntimeError("Перезапустите установщик после установки Python.")
        self._ll(f">> Python: {python}")
        self._mark(0, "done")
        self._log("Python ✓", 0.20)

        # Step 1: Download
        self._mark(1, "active")
        self._ll(">> Скачивание с GitHub...")
        zp = os.path.join(tmp, "src.zip")
        urllib.request.urlretrieve(
            GITHUB_ZIP, zp,
            reporthook=lambda b, bs, ts: self._log(
                f"Скачивание: {min(b*bs,max(ts,1))//1024} КБ",
                0.22 + 0.14*(b*bs/max(ts,1))
            )
        )
        self._ll(">> Распаковка...")
        with zipfile.ZipFile(zp) as z:
            z.extractall(tmp)
        extracted = next(
            (os.path.join(tmp, d) for d in os.listdir(tmp)
             if os.path.isdir(os.path.join(tmp, d)) and d.upper().startswith("FIST")),
            None
        )
        if not extracted:
            raise RuntimeError("Распакованные файлы не найдены.")
        src = os.path.join(install_dir, "src")
        if os.path.exists(src):
            shutil.rmtree(src)
        shutil.copytree(extracted, src)
        self._ll(f">> Исходники: {src}")
        self._mark(1, "done")
        self._log("Исходники ✓", 0.38)

        # Step 2: Deps — parallel-ish (sequential but fast)
        self._mark(2, "active")
        pkgs = [("pip",0.42),("pyautogui",0.49),("pynput",0.55),
                ("pillow",0.61),("pyinstaller",0.67)]
        for pkg, pct in pkgs:
            self._log(f"pip install {pkg}...", pct)
            self._ll(f">> pip install {pkg}")
            args = ["--upgrade", pkg] if pkg == "pip" else [pkg]
            pip_install(python, args)
            self._ll(f"   {pkg} ✓")
        self._mark(2, "done")
        self._log("Зависимости ✓", 0.68)

        # Step 3: Build — live log via Popen
        self._mark(3, "active")
        self._log("Сборка EXE... смотрите лог ↓", 0.70)
        self._ll("=" * 46)
        self._ll(">> PyInstaller запущен (2–5 мин)")
        self._ll("=" * 46)

        spec_f = os.path.join(src, "fist_click.spec")
        py_f   = os.path.join(src, "fist_click.py")

        if os.path.exists(spec_f):
            cmd = [
                python, "-m", "PyInstaller", "--noconfirm",
                "--distpath", install_dir,
                "--workpath", os.path.join(tmp, "build"),
                spec_f,
            ]
            self._ll(">> Режим: .spec")
        else:
            cmd = [
                python, "-m", "PyInstaller", "--noconfirm",
                "--onefile", "--windowed", "--name", "FIST_CLICK",
                "--distpath", install_dir,
                "--workpath", os.path.join(tmp, "build"),
                "--specpath", tmp,
                py_f,
            ]
            self._ll(">> Режим: .py (onefile)")

        self._ll(f">> {' '.join(str(c) for c in cmd)}")
        self._ll("=" * 46)

        CNW = 0x08000000 if os.name == "nt" else 0
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            cwd=src, creationflags=CNW,
        )
        pct_b = 0.70
        phases = {
            "Analysis":  (0.73, "Анализ..."),
            "Building":  (0.79, "Компиляция..."),
            "Collecting":(0.83, "Сбор..."),
            "EXE":       (0.88, "Упаковка EXE..."),
        }
        for raw in proc.stdout:
            line = raw.rstrip()
            if not line:
                continue
            self._ll(line)
            for kw, (p, m) in phases.items():
                if kw in line and p > pct_b:
                    pct_b = p
                    self._log(m, p)
                    break
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("PyInstaller завершился с ошибкой.\nСм. лог выше.")

        self._ll("=" * 46)
        self._ll(">> Сборка завершена ✓")
        self._ll("=" * 46)

        exe_name = "FIST_CLICK.exe"
        exe_path = os.path.join(install_dir, exe_name)
        if not os.path.exists(exe_path):
            for rd, _, files in os.walk(install_dir):
                for ffile in files:
                    if ffile.upper() == exe_name.upper() and "_tmp" not in rd:
                        found = os.path.join(rd, ffile)
                        if os.path.normpath(found) != os.path.normpath(exe_path):
                            shutil.copy2(found, exe_path)
                        break
        if not os.path.exists(exe_path):
            raise RuntimeError(f"FIST_CLICK.exe не найден.\nПуть: {install_dir}")

        self._ll(f">> EXE: {exe_path}")
        self._mark(3, "done")
        self._log("EXE собран ✓", 0.88)

        # Step 4: Shortcuts
        self._mark(4, "active")
        self._log("Ярлыки...", 0.91)
        self._ll(">> Создание ярлыков...")
        try:
            try:
                import winshell
            except ImportError:
                pip_install(python, ["winshell", "pywin32"])
                import winshell
            from win32com.client import Dispatch
            shell = Dispatch("WScript.Shell")
            if self._shortcut_var.get():
                lnk = os.path.join(winshell.desktop(), "FIST CLICK.lnk")
                sc = shell.CreateShortCut(lnk)
                sc.Targetpath = exe_path
                sc.WorkingDirectory = install_dir
                sc.Description = "FIST CLICK v2 Auto Clicker"
                sc.save()
                self._ll("   Рабочий стол ✓")
            if self._startmenu_var.get():
                sm = os.path.join(os.environ.get("APPDATA",""),
                                  r"Microsoft\Windows\Start Menu\Programs\FIST CLICK")
                os.makedirs(sm, exist_ok=True)
                lnk = os.path.join(sm, "FIST CLICK.lnk")
                sc = shell.CreateShortCut(lnk)
                sc.Targetpath = exe_path
                sc.WorkingDirectory = install_dir
                sc.save()
                self._ll("   Меню Пуск ✓")
        except Exception as e:
            self._ll(f"   Ярлыки пропущены: {e}")

        self._mark(4, "done")
        self._log("Установка завершена!", 1.0)
        self._ll(">> Всё готово!")
        shutil.rmtree(tmp, ignore_errors=True)
        self._ui(lambda: self._done(exe_path))

    # ─────────────────────────────────────────────────────────────────────────
    def _done(self, exe_path):
        self._install_btn.config(
            text="✓  ОТКРЫТЬ FIST CLICK",
            bg=C["green"], state="normal",
            command=lambda: os.startfile(exe_path),
        )
        self._prog_lbl.config(
            text="Установка завершена! Нажмите для запуска.",
            fg=C["green"],
        )
        messagebox.showinfo("FIST CLICK",
                            f"Установка завершена!\n\n{exe_path}")

    def _on_error(self, msg):
        self._install_btn.config(state="normal",
                                 text="▶  УСТАНОВИТЬ",
                                 bg=C["accent"])
        self._prog_lbl.config(text="Ошибка установки", fg=C["accent"])
        for dot, lbl in self._step_labels:
            if dot.cget("text") == "◉":
                dot.config(text="✗", fg=C["accent"])
                lbl.config(fg=C["accent"])
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n\n{msg}")


if __name__ == "__main__":
    Installer()
