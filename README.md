# 👊 FIST CLICK

> Lightweight auto clicker with multi-spot support, coordinate picker, hotkey toggle, and dark UI.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Features

| Feature | Details |
|---|---|
| **Up to 4 click spots** | Each spot independently toggled ON/OFF |
| **Coordinate picker** | Fullscreen crosshair overlay — click to capture X/Y |
| **Mouse button** | LEFT or RIGHT per spot |
| **Click type** | Single (×1) or Double (×2) per spot |
| **Interval** | h : m : s : ms |
| **Duration mode** | INFINITE (until STOP) or TIMER (auto-stop) |
| **Hotkey** | Default F6, reassignable via SET button |
| **Always on top** | Window stays above all other apps |
| **Click counter** | Live count displayed in UI |

---

## Quick Start

### Run from source

```bash
pip install pyautogui pynput pillow
python fist_click.py
```

### Build .exe (Windows)

```bash
pip install pyinstaller pyautogui pynput pillow
pyinstaller fist_click.spec
```

The ready `FIST_CLICK.exe` will appear in the `dist/` folder.

---

## Usage

1. Click **⊕ PICK** on any spot card, then click anywhere on your screen to set coordinates
2. Choose **LEFT / RIGHT** mouse button and **×1 / ×2** click type per spot
3. Set the **INTERVAL** between click cycles
4. Choose **INFINITE** or **TIMER** mode
5. Press **▶ START** or press **F6** to begin clicking
6. Press **■ STOP** or press **F6** again to stop

---

## Notes

- If the global hotkey (F6) doesn't respond, try running as **Administrator**
- To run as admin by default in the .exe, set `uac_admin=True` in `fist_click.spec` before building
- Minimum interval is clamped to 50ms to prevent runaway loops

---

## Requirements

- Python 3.8+
- `pyautogui`
- `pynput`
- `pillow`
- `tkinter` (included with Python on Windows)
