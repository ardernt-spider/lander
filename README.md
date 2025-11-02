# Lunar Lander (Pygame Zero)

A small Lunar Lander clone implemented using Pygame Zero. The game draws the lander procedurally (no external assets).

Requirements

- Python 3.8+
- Pygame Zero (install with pip)

Install

```powershell
python -m pip install -r requirements.txt
```

Run

```powershell
# preferred: uses the pgzrun script
pgzrun main.py

# alternative if pgzrun isn't on PATH
python -m pgzero main.py
```

Controls

- Left / Right: rotate
- Up / Space: main thrust
- R: reset

Notes

- This is a small, educational demo. Feel free to request additions (sound, images, better landing detection, particles, scoring, levels).

## Build & Release

Local build (Windows PowerShell):

```powershell
# activate virtualenv (example)
& .\.venv\Scripts\Activate.ps1
# install runtime & build deps
python -m pip install -r requirements.txt
# run the build helper (uses PyInstaller via build.py)
python .\build.py
# built artifacts are written to the `dist\` folder
```
