"""
FIST CLICK — Установщик v1.0.3
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
import winreg

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


def pip_install(python, packages):
    result = subprocess.run(
        [python, "-m", "pip", "install", "--upgrade", *packages],
        capture_output=True, text=True, timeout=300,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pip error:\n{result.stderr[-500:]}")


# ─────────────────────────────────────────────────────────────────────────────
#  PROGRESS BAR
# ─────────────────────────────────────────────────────────────────────────────

class ProgressBar(tk.Canvas):
    def __init__(self, parent, **kw):
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
#  LOG BOX
# ─────────────────────────────────────────────────────────────────────────────

class LogBox(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1, **kw)
        self._text = tk.Text(
            self, height=7,
            font=("Courier New", 8),
            fg=C["text2"], bg=C["card"],
            relief="flat", bd=0,
            state="disabled",
            wrap="char",
            insertbackground=C["text"],
        )
        sb = tk.Scrollbar(self, command=self._text.yview,
                          bg=C["border"], troughcolor=C["card"],
                          activebackground=C["text3"],
                          relief="flat", bd=0, width=8)
        self._text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._text.pack(side="left", fill="both", expand=True, padx=6, pady=4)

    def append(self, line: str):
        def _do():
            self._text.configure(state="normal")
            self._text.insert("end", line + "\n")
            self._text.see("end")
            self._text.configure(state="disabled")
        try:
            self._text.after(0, _do)
        except Exception:
            pass

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def get_all(self) -> str:
        return self._text.get("1.0", "end")


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
        self._center(520, 700)
        self._build_ui()
        self.root.mainloop()

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _copy_to_clipboard(self, text: str, btn: tk.Button = None):
        """Скопировать текст в буфер обмена и мигнуть кнопкой."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        if btn:
            orig = btn.cget("text")
            btn.config(text="\u2713 Скопировано", fg=C["green"])
            self.root.after(1500, lambda: btn.config(text=orig, fg=C["text2"]))

    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # Заголовок
        hdr = tk.Frame(root, bg=C["bg"], pady=16)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text="FIST", font=("Courier New", 24, "bold"),
                 fg=C["accent"], bg=C["bg"]).pack(side="left")
        tk.Label(hdr, text=" CLICK", font=("Courier New", 24, "bold"),
                 fg=C["text"], bg=C["bg"]).pack(side="left")
        tk.Label(hdr, text="  УСТАНОВЩИК", font=("Courier New", 9),
                 fg=C["text2"], bg=C["bg"]).pack(side="left", pady=(6, 0))
        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 14))

        # Папка установки
        tk.Label(root, text="ПАПКА УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(anchor="w", padx=24)
        path_row = tk.Frame(root, bg=C["bg"])
        path_row.pack(fill="x", padx=24, pady=(5, 12))
        self.path_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "FIST-CLICK")
        )
        tk.Entry(path_row, textvariable=self.path_var,
                 font=("Courier New", 10), fg=C["text"], bg=C["card"],
                 insertbackground=C["text"], relief="flat", bd=0,
                 highlightbackground=C["border"], highlightthickness=1,
                 ).pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))

        # Кнопка копировать путь
        self._copy_path_btn = tk.Button(
            path_row, text="\u29c9",
            font=("Courier New", 11), fg=C["text2"], bg=C["card"],
            activebackground=C["border"], relief="flat", bd=0,
            padx=8, pady=5, cursor="hand2",
            command=lambda: self._copy_to_clipboard(self.path_var.get(), self._copy_path_btn),
        )
        self._copy_path_btn.pack(side="left", padx=(0, 6))

        tk.Button(path_row, text="\U0001f4c1",
                  font=("Courier New", 11), fg=C["text"], bg=C["card"],
                  activebackground=C["border"], relief="flat", bd=0,
                  padx=10, pady=5, cursor="hand2", command=self._browse,
                  ).pack(side="left")

        # Опции
        self.shortcut_var  = tk.BooleanVar(value=True)
        self.startmenu_var = tk.BooleanVar(value=True)
        opts = tk.Frame(root, bg=C["bg"])
        opts.pack(fill="x", padx=24, pady=(0, 14))
        for var, text in [
            (self.shortcut_var,  "Создать ярлык на рабочем столе"),
            (self.startmenu_var, "Добавить в меню Пуск"),
        ]:
            row = tk.Frame(opts, bg=C["bg"])
            row.pack(fill="x", pady=2)
            tk.Checkbutton(row, variable=var, text=text,
                           font=("Courier New", 9), fg=C["text"], bg=C["bg"],
                           selectcolor=C["bg"], activebackground=C["bg"],
                           relief="flat", bd=0, cursor="hand2",
                           ).pack(side="left")

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 14))

        # Шаги
        tk.Label(root, text="ЭТАПЫ УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(anchor="w", padx=24)
        self.step_labels = []
        steps_frame = tk.Frame(root, bg=C["bg"])
        steps_frame.pack(fill="x", padx=24, pady=(6, 12))
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

        # Прогресс
        self.progress = ProgressBar(root, bg=C["bar_bg"])
        self.progress.pack(fill="x", padx=24, pady=(0, 4))
        self.progress_lbl = tk.Label(root, text="Готов к установке",
                                     font=("Courier New", 8),
                                     fg=C["text2"], bg=C["bg"])
        self.progress_lbl.pack(anchor="w", padx=24, pady=(0, 10))

        # Лог — шапка с кнопкой копирования
        log_hdr = tk.Frame(root, bg=C["bg"])
        log_hdr.pack(fill="x", padx=24, pady=(0, 4))
        tk.Label(log_hdr, text="ЛОГ УСТАНОВКИ",
                 font=("Courier New", 8, "bold"), fg=C["text2"], bg=C["bg"]
                 ).pack(side="left")
        tk.Label(log_hdr, text="(прогресс сборки в реальном времени)",
                 font=("Courier New", 7), fg=C["text3"], bg=C["bg"]
                 ).pack(side="left", padx=(8, 0))

        # Кнопка «Копировать лог» — справа в шапке
        self._copy_log_btn = tk.Button(
            log_hdr, text="\u29c9 Копировать лог",
            font=("Courier New", 7), fg=C["text2"], bg=C["bg"],
            activebackground=C["bg"], activeforeground=C["green"],
            relief="flat", bd=0, padx=4, pady=0,
            cursor="hand2",
            command=self._do_copy_log,
        )
        self._copy_log_btn.pack(side="right")

        self.logbox = LogBox(root)
        self.logbox.pack(fill="x", padx=24, pady=(0, 12))

        tk.Frame(root, bg=C["border"], height=1).pack(fill="x", padx=24, pady=(0, 14))

        self.install_btn = tk.Button(
            root, text="\u25b6  УСТАНОВИТЬ",
            font=("Courier New", 13, "bold"),
            fg=C["bg"], bg=C["green"],
            activebackground="#25A244", activeforeground=C["bg"],
            relief="flat", bd=0, pady=12,
            cursor="hand2", command=self._start_install,
        )
        self.install_btn.pack(fill="x", padx=24, pady=(0, 20))

    # ─────────────────────────────────────────────────────────────────────────

    def _do_copy_log(self):
        self._copy_to_clipboard(self.logbox.get_all(), self._copy_log_btn)

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

    def _ui(self, fn):
        self.root.after(0, fn)

    def _log(self, msg, pct=None):
        def _do():
            self.progress_lbl.config(text=msg)
            if pct is not None:
                self.progress.set(pct)
        self._ui(_do)

    def _mark_step(self, index, state):
        self._ui(lambda: self._set_step(index, state))

    def _logline(self, line: str):
        self.logbox.append(line)

    # ─────────────────────────────────────────────────────────────────────────

    def _start_install(self):
        self.install_btn.config(state="disabled", text="Установка\u2026")
        self.logbox.clear()
        threading.Thread(target=self._install, daemon=True).start()

    def _install(self):
        try:
            self._run_install(self.path_var.get().strip())
        except Exception as e:
            self._ui(lambda: self._on_error(str(e)))

    def _run_install(self, install_dir):
        os.makedirs(install_dir, exist_ok=True)
        temp_dir = os.path.join(install_dir, "_tmp")
        os.makedirs(temp_dir, exist_ok=True)

        # ── Шаг 0: Python ────────────────────────────────────────────────────
        self._mark_step(0, "active")
        self._log("Поиск Python...", 0.02)
        self._logline(">> Поиск Python в системе...")
        python = find_python()
        if python is None:
            self._logline(">> Python не найден, скачиваем...")
            self._log("Скачивание Python...", 0.05)
            py_exe = os.path.join(temp_dir, "python_setup.exe")
            urllib.request.urlretrieve(
                "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
                py_exe,
                reporthook=lambda b, bs, ts: self._log(
                    f"Python: {min(b*bs, ts)//1024}/{ts//1024} КБ",
                    0.05 + 0.1 * (b * bs / max(ts, 1))
                )
            )
            self._logline(">> Установка Python...")
            subprocess.run(
                [py_exe, "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1"],
                check=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            python = find_python()
            if python is None:
                raise RuntimeError("Повторно запустите установщик после установки Python.")
        self._logline(f">> Python: {python}")
        self._mark_step(0, "done")
        self._log("Python найден \u2713", 0.20)

        # ── Шаг 1: Исходники ─────────────────────────────────────────────────
        self._mark_step(1, "active")
        self._logline(">> Скачивание с GitHub...")
        zip_path = os.path.join(temp_dir, "src.zip")
        urllib.request.urlretrieve(
            GITHUB_ZIP, zip_path,
            reporthook=lambda b, bs, ts: self._log(
                f"GitHub: {min(b*bs, max(ts, 1))//1024} КБ",
                0.22 + 0.14 * (b * bs / max(ts, 1))
            )
        )
        self._logline(">> Распаковка...")
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
        self._logline(f">> Исходники: {src_dir}")
        self._mark_step(1, "done")
        self._log("Исходники скачаны \u2713", 0.38)

        # ── Шаг 2: Зависимости ───────────────────────────────────────────────
        self._mark_step(2, "active")
        for pkg, pct, label in [
            ("pip",         0.42, "pip"),
            ("pyautogui",   0.48, "pyautogui"),
            ("pynput",      0.54, "pynput"),
            ("pillow",      0.60, "pillow"),
            ("pyinstaller", 0.66, "pyinstaller"),
        ]:
            self._log(f"Установка {label}...", pct)
            self._logline(f">> pip install {label}")
            args = ["--upgrade", pkg] if pkg == "pip" else [pkg]
            pip_install(python, args)
            self._logline(f"   {label} \u2713")
        self._mark_step(2, "done")
        self._log("Зависимости установлены \u2713", 0.68)

        # ── Шаг 3: Сборка EXE ────────────────────────────────────────────────
        self._mark_step(3, "active")
        self._log("Сборка EXE... смотрите лог \u2193", 0.70)
        self._logline("=" * 48)
        self._logline(">> PyInstaller запущен (2-5 мин)...")
        self._logline("=" * 48)

        spec_path = os.path.join(src_dir, "fist_click.spec")
        py_path   = os.path.join(src_dir, "fist_click.py")

        # ВАЖНО: при передаче .spec нельзя использовать --specpath
        # Поэтому выбираем стратегию в зависимости от того, что есть
        if os.path.exists(spec_path):
            # Со .spec файлом — только --distpath и --workpath
            cmd = [
                python, "-m", "PyInstaller", "--noconfirm",
                "--distpath", install_dir,
                "--workpath", os.path.join(temp_dir, "build"),
                spec_path,
            ]
            self._logline(f">> Режим: .spec файл")
        else:
            # Без .spec — можно передавать все флаги
            cmd = [
                python, "-m", "PyInstaller", "--noconfirm",
                "--onefile", "--windowed",
                "--name", "FIST_CLICK",
                "--distpath", install_dir,
                "--workpath", os.path.join(temp_dir, "build"),
                "--specpath", temp_dir,
                py_path,
            ]
            self._logline(f">> Режим: fist_click.py (без .spec)")

        self._logline(f">> CMD: {' '.join(cmd)}")
        self._logline("=" * 48)

        CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=src_dir,
            creationflags=CREATE_NO_WINDOW,
        )

        pct_build = 0.70
        phase_map = {
            "Analysis":   (0.73, "Анализ зависимостей..."),
            "Building":   (0.79, "Компиляция..."),
            "Collecting": (0.83, "Сборка пакетов..."),
            "EXE":        (0.88, "Упаковка EXE..."),
            "PKG":        (0.85, "Упаковка PKG..."),
            "COLLECT":    (0.86, "Сбор файлов..."),
        }
        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            if not line:
                continue
            self._logline(line)
            for keyword, (pct, msg) in phase_map.items():
                if keyword in line and pct > pct_build:
                    pct_build = pct
                    self._log(msg, pct_build)
                    break

        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(
                "PyInstaller завершился с ошибкой.\n"
                "Скопируйте лог кнопкой выше и проверьте детали."
            )

        self._logline("=" * 48)
        self._logline(">> Сборка завершена \u2713")
        self._logline("=" * 48)

        # Найти exe — PyInstaller кладёт его в distpath/FIST_CLICK/FIST_CLICK.exe
        # или прямо в distpath если --onefile
        exe_name = "FIST_CLICK.exe"
        exe_path = os.path.join(install_dir, exe_name)
        if not os.path.exists(exe_path):
            for rd, _, files in os.walk(install_dir):
                for f in files:
                    if f.upper() == exe_name.upper() and "_tmp" not in rd:
                        found = os.path.join(rd, f)
                        if os.path.normpath(found) != os.path.normpath(exe_path):
                            shutil.copy2(found, exe_path)
                        break

        if not os.path.exists(exe_path):
            raise RuntimeError(
                f"FIST_CLICK.exe не найден в {install_dir}\n"
                "Проверьте лог — возможно PyInstaller создал другую структуру."
            )

        self._logline(f">> EXE: {exe_path}")
        self._mark_step(3, "done")
        self._log("EXE собран \u2713", 0.88)

        # ── Шаг 4: Ярлыки ────────────────────────────────────────────────────
        self._mark_step(4, "active")
        self._log("Создание ярлыков...", 0.91)
        self._logline(">> Создание ярлыков...")
        try:
            try:
                import winshell
            except ImportError:
                self._logline(">> pip install winshell pywin32")
                pip_install(python, ["winshell", "pywin32"])
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
                self._logline("   Ярлык на рабочем столе \u2713")
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
                self._logline("   Меню Пуск \u2713")
        except Exception as e:
            self._logline(f"   Ярлыки пропущены: {e}")

        self._mark_step(4, "done")
        self._log("Установка завершена!", 1.0)
        self._logline(">> Готово!")

        shutil.rmtree(temp_dir, ignore_errors=True)
        self._ui(lambda: self._on_done(exe_path))

    # ─────────────────────────────────────────────────────────────────────────

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
            f"Установка завершена!\n\nFIST_CLICK.exe:\n{exe_path}"
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
