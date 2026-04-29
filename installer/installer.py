"""
FIST CLICK — Установщик
Скачивает, устанавливает зависимости и собирает FIST_CLICK.exe
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import os
import zipfile
import shutil
import urllib.request
import winreg  # Windows only

# ─────────────────────────────────────────────────────────────────────────────
REPO_OWNER = "Achinsky"
REPO_NAME  = "FIST-CLICK"
GITHUB_ZIP = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/main.zip"

C = {
    "bg":     "#0D0D0D",
    "card":   "#1A1A1A",
    "border": "#2A2A2A",
    "accent": "#FF3B30",
    "green":  "#30D158",
    "text":   "#FFFFFF",
    "text2":  "#8A8A8E",
    "text3":  "#48484A",
    "bar_bg": "#2C2C2E",
}

# ─────────────────────────────────────────────────────────────────────────────

def find_python():
    """Finds python.exe in PATH and Windows registry."""
    for cmd in ("py", "python", "python3"):
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and "Python 3" in r.stdout + r.stderr:
                return cmd
        except Exception:
            pass
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for sub in (
            r"SOFTWARE\Python\PythonCore",
            r"SOFTWARE\WOW6432Node\Python\PythonCore",
        ):
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


def pip_install(python, packages, log_fn):
    log_fn(f"  pip install {' '.join(packages)}")
    result = subprocess.run(
        [python, "-m", "pip", "install", "--upgrade", *packages],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip error:\n{result.stderr[-500:]}")


# ─────────────────────────────────────────────────────────────────────────────
#  PROGRESS BAR
# ─────────────────────────────────────────────────────────────────────────────

class ProgressBar(tk.Canvas):
    """Градиентный прогресс-бар на Canvas.
    bg НЕ передаётся в __init__ — берётся из kw или дефолт bar_bg.
    """
    def __init__(self, parent, **kw):
        # Извлекаем bg из kw чтобы не было конфликта при передаче в super()
        bg = kw.pop("bg", C["bar_bg"])
        super().__init__(parent, height=6, bg=bg, highlightthickness=0, **kw)
        self._pct = 0
        self.bind("<Configure>", lambda e: self._redraw())

    def set(self, pct: float):
        self._pct = max(0.0, min(1.0, pct))
        self._redraw()

    def _redraw(self):
        self.delete("all")
        w = self.winfo_width()
        filled = int(w * self._pct)
        for x in range(filled):
            ratio = x / max(w, 1)
            r = int(0xFF * (1 - ratio) + 0x30 * ratio)
            g = int(0x3B * (1 - ratio) + 0xD1 * ratio)
            b = int(0x30 * (1 - ratio) + 0x58 * ratio)
            self.create_line(x, 0, x, 6, fill=f"#{r:02x}{g:02x}{b:02x}")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN INSTALLER
# ─────────────────────────────────────────────────────────────────────────────

class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FIST CLICK — Установщик")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self._center(500, 560)
        self._build_ui()
        self.root.mainloop()

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        root = self.root

        # ── Заголовок ────────────────────────────────────────────────────────
        hdr = tk.Frame(root, bg=C["bg"], pady=20)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text="FIST", font=("Courier New", 26, "bold"),
                 fg=C["accent"], bg=C["bg"]).pack(side="left")
        tk.Label(hdr, text=" CLICK", font=("Courier New", 26, "bold"),
                 fg=C["text"], bg=C["bg"]).pack(side="left")
        tk.Label(hdr, text="  УСТАНОВЩИК", font=("Courier New", 10),
                 fg=C["text2"], bg=C["bg"]).pack(side="left", pady=(8, 0))

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 18))

        # ── Папка установки ──────────────────────────────────────────────────
        tk.Label(root, text="ПАПКА УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(anchor="w", padx=24)

        path_row = tk.Frame(root, bg=C["bg"])
        path_row.pack(fill="x", padx=24, pady=(6, 18))

        self.path_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "FIST-CLICK")
        )
        tk.Entry(path_row, textvariable=self.path_var,
                 font=("Courier New", 10), fg=C["text"], bg=C["card"],
                 insertbackground=C["text"], relief="flat", bd=0,
                 highlightbackground=C["border"], highlightthickness=1,
                 ).pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        tk.Button(path_row, text="\U0001f4c1",
                  font=("Courier New", 11), fg=C["text"], bg=C["card"],
                  activebackground=C["border"], relief="flat", bd=0,
                  padx=10, pady=5, cursor="hand2", command=self._browse,
                  ).pack(side="left")

        # ── Опции ────────────────────────────────────────────────────────────
        self.shortcut_var  = tk.BooleanVar(value=True)
        self.startmenu_var = tk.BooleanVar(value=True)
        opts = tk.Frame(root, bg=C["bg"])
        opts.pack(fill="x", padx=24, pady=(0, 18))
        for var, text in [
            (self.shortcut_var,  "Создать ярлык на рабочем столе"),
            (self.startmenu_var, "Добавить в меню Пуск"),
        ]:
            row = tk.Frame(opts, bg=C["bg"])
            row.pack(fill="x", pady=3)
            tk.Checkbutton(row, variable=var, text=text,
                           font=("Courier New", 9), fg=C["text"], bg=C["bg"],
                           selectcolor=C["bg"], activebackground=C["bg"],
                           relief="flat", bd=0, cursor="hand2",
                           ).pack(side="left")

        # ── Шаги установки ───────────────────────────────────────────────────
        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 18))
        tk.Label(root, text="ЭТАПЫ УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(anchor="w", padx=24)

        self.step_labels = []
        steps_frame = tk.Frame(root, bg=C["bg"])
        steps_frame.pack(fill="x", padx=24, pady=(8, 18))
        for text in [
            "Проверка Python",
            "Скачивание FIST CLICK с GitHub",
            "Установка зависимостей",
            "Сборка FIST_CLICK.exe",
            "Создание ярлыков",
        ]:
            row = tk.Frame(steps_frame, bg=C["bg"])
            row.pack(fill="x", pady=2)
            dot = tk.Label(row, text="\u25cb", font=("Courier New", 11),
                           fg=C["text3"], bg=C["bg"], width=2)
            dot.pack(side="left")
            lbl = tk.Label(row, text=text, font=("Courier New", 9),
                           fg=C["text3"], bg=C["bg"], anchor="w")
            lbl.pack(side="left")
            self.step_labels.append((dot, lbl))

        # ── Прогресс-бар ─────────────────────────────────────────────────────
        # bg передаётся один раз — через kw, внутри ProgressBar извлекается pop()
        self.progress = ProgressBar(root, bg=C["bar_bg"])
        self.progress.pack(fill="x", padx=24, pady=(0, 6))

        self.progress_lbl = tk.Label(root, text="Готов к установке",
                                     font=("Courier New", 8),
                                     fg=C["text2"], bg=C["bg"])
        self.progress_lbl.pack(anchor="w", padx=24, pady=(0, 18))

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 18))

        # ── Кнопка установки ─────────────────────────────────────────────────
        self.install_btn = tk.Button(
            root, text="\u25b6  УСТАНОВИТЬ",
            font=("Courier New", 13, "bold"),
            fg=C["bg"], bg=C["green"],
            activebackground="#25A244", activeforeground=C["bg"],
            relief="flat", bd=0, pady=13,
            cursor="hand2", command=self._start_install,
        )
        self.install_btn.pack(fill="x", padx=24, pady=(0, 20))

    # ── Вспомогательные методы ───────────────────────────────────────────────

    def _browse(self):
        path = filedialog.askdirectory(title="Выберите папку установки")
        if path:
            self.path_var.set(path)

    def _set_step(self, index, state):
        dot, lbl = self.step_labels[index]
        cfg = {
            "wait":   ("\u25cb", C["text3"], C["text3"]),
            "active": ("\u25c9", C["accent"], C["text"]),
            "done":   ("\u2713", C["green"],  C["text"]),
            "error":  ("\u2717", C["accent"], C["accent"]),
        }[state]
        dot.config(text=cfg[0], fg=cfg[1])
        lbl.config(fg=cfg[2])

    def _log(self, msg, pct=None):
        def _do():
            self.progress_lbl.config(text=msg)
            if pct is not None:
                self.progress.set(pct)
        self.root.after(0, _do)

    def _mark_step(self, index, state):
        self.root.after(0, lambda: self._set_step(index, state))

    # ── Установка ────────────────────────────────────────────────────────────

    def _start_install(self):
        self.install_btn.config(state="disabled", text="Установка\u2026")
        threading.Thread(target=self._install, daemon=True).start()

    def _install(self):
        install_dir = self.path_var.get().strip()
        try:
            self._run_install(install_dir)
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _run_install(self, install_dir):
        os.makedirs(install_dir, exist_ok=True)
        temp_dir = os.path.join(install_dir, "_tmp")
        os.makedirs(temp_dir, exist_ok=True)

        # Шаг 0: Python
        self._mark_step(0, "active")
        self._log("Поиск Python...", 0.02)
        python = find_python()
        if python is None:
            self._log("Скачивание Python...", 0.05)
            py_exe = os.path.join(temp_dir, "python_setup.exe")
            urllib.request.urlretrieve(
                "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
                py_exe,
                reporthook=lambda b, bs, ts: self._log(
                    f"Скачивание Python: {min(b*bs, ts)//1024}/{ts//1024} КБ",
                    0.05 + 0.1 * (b * bs / max(ts, 1))
                )
            )
            self._log("Установка Python...", 0.15)
            subprocess.run(
                [py_exe, "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1"],
                check=True, timeout=300
            )
            python = find_python()
            if python is None:
                raise RuntimeError("Повторно запустите установщик после установки Python.")
        self._mark_step(0, "done")
        self._log("Python найден \u2713", 0.20)

        # Шаг 1: Скачать исходники
        self._mark_step(1, "active")
        self._log("Скачивание с GitHub...", 0.22)
        zip_path = os.path.join(temp_dir, "src.zip")
        urllib.request.urlretrieve(
            GITHUB_ZIP, zip_path,
            reporthook=lambda b, bs, ts: self._log(
                f"Скачивание: {min(b*bs, max(ts, 1))//1024} КБ",
                0.22 + 0.14 * (b * bs / max(ts, 1))
            )
        )
        self._log("Распаковка...", 0.37)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(temp_dir)
        extracted = next(
            (os.path.join(temp_dir, d) for d in os.listdir(temp_dir)
             if os.path.isdir(os.path.join(temp_dir, d)) and d.upper().startswith("FIST")),
            None
        )
        if not extracted:
            raise RuntimeError("Не найдены распакованные файлы.")
        src_dir = os.path.join(install_dir, "src")
        if os.path.exists(src_dir):
            shutil.rmtree(src_dir)
        shutil.copytree(extracted, src_dir)
        self._mark_step(1, "done")
        self._log("Исходники скачаны \u2713", 0.38)

        # Шаг 2: Зависимости
        self._mark_step(2, "active")
        for pkg, pct, msg in [
            ("pip",         0.42, "pip..."),
            ("pyautogui",   0.48, "pyautogui..."),
            ("pynput",      0.54, "pynput..."),
            ("pillow",      0.60, "pillow..."),
            ("pyinstaller", 0.66, "pyinstaller..."),
        ]:
            self._log(f"Установка {msg}", pct)
            args = ["--upgrade", pkg] if pkg == "pip" else [pkg]
            pip_install(python, args, lambda m: None)
        self._mark_step(2, "done")
        self._log("Зависимости установлены \u2713", 0.68)

        # Шаг 3: Сборка exe
        self._mark_step(3, "active")
        self._log("Сборка FIST_CLICK.exe... (1-3 мин)", 0.70)
        spec = os.path.join(src_dir, "fist_click.spec")
        py   = os.path.join(src_dir, "fist_click.py")
        build_src = spec if os.path.exists(spec) else py
        res = subprocess.run(
            [python, "-m", "PyInstaller", "--noconfirm",
             "--distpath", install_dir,
             "--workpath", os.path.join(temp_dir, "build"),
             "--specpath", temp_dir,
             build_src],
            capture_output=True, text=True, timeout=600, cwd=src_dir
        )
        if res.returncode != 0:
            raise RuntimeError(f"PyInstaller ошибка:\n{res.stderr[-600:]}")
        exe_name = "FIST_CLICK.exe"
        exe_path = os.path.join(install_dir, exe_name)
        if not os.path.exists(exe_path):
            for rd, _, files in os.walk(install_dir):
                for f in files:
                    if f == exe_name:
                        shutil.copy2(os.path.join(rd, f), exe_path)
                        break
        if not os.path.exists(exe_path):
            raise RuntimeError("FIST_CLICK.exe не найден после сборки.")
        self._mark_step(3, "done")
        self._log("EXE собран \u2713", 0.88)

        # Шаг 4: Ярлыки
        self._mark_step(4, "active")
        self._log("Создание ярлыков...", 0.91)
        try:
            try:
                import winshell
            except ImportError:
                pip_install(python, ["winshell", "pywin32"], lambda m: None)
                import winshell
            from win32com.client import Dispatch
            shell = Dispatch("WScript.Shell")
            if self.shortcut_var.get():
                lnk = os.path.join(winshell.desktop(), "FIST CLICK.lnk")
                sc = shell.CreateShortCut(lnk)
                sc.Targetpath = exe_path
                sc.WorkingDirectory = install_dir
                sc.Description = "FIST CLICK Auto Clicker"
                sc.save()
            if self.startmenu_var.get():
                sm = os.path.join(
                    os.environ.get("APPDATA", ""),
                    r"Microsoft\Windows\Start Menu\Programs\FIST CLICK"
                )
                os.makedirs(sm, exist_ok=True)
                lnk = os.path.join(sm, "FIST CLICK.lnk")
                sc = shell.CreateShortCut(lnk)
                sc.Targetpath = exe_path
                sc.WorkingDirectory = install_dir
                sc.save()
        except Exception:
            pass  # ярлыки опциональны
        self._mark_step(4, "done")
        self._log("Ярлыки созданы \u2713", 1.0)

        shutil.rmtree(temp_dir, ignore_errors=True)
        self.root.after(0, lambda: self._on_done(exe_path))

    # ── Финал ────────────────────────────────────────────────────────────────

    def _on_done(self, exe_path):
        self.install_btn.config(
            text="\u2713  ОТКРЫТЬ FIST CLICK",
            bg=C["green"], state="normal",
            command=lambda: os.startfile(exe_path),
        )
        self.progress_lbl.config(
            text="Установка завершена! Нажмите для запуска.",
            fg=C["green"]
        )
        messagebox.showinfo(
            "FIST CLICK установлен",
            f"Установка завершена!\n\nFIST_CLICK.exe находится в:\n{os.path.dirname(exe_path)}"
        )

    def _on_error(self, msg):
        self.install_btn.config(
            state="normal",
            text="\u25b6  УСТАНОВИТЬ",
            bg=C["accent"]
        )
        self.progress_lbl.config(text="Ошибка установки", fg=C["accent"])
        for dot, lbl in self.step_labels:
            if dot.cget("text") == "\u25c9":
                dot.config(text="\u2717", fg=C["accent"])
                lbl.config(fg=C["accent"])
        messagebox.showerror("Ошибка установки", f"Произошла ошибка:\n\n{msg}")


if __name__ == "__main__":
    Installer()
