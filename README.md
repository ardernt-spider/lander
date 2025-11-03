# Lunar Lander (Pygame Zero)

A small Lunar Lander clone implemented using Pygame Zero.

Requirements

- Python 3.8+
- Pygame Zero (install with pip)

Credits:

## Credits

### Coding
	-- "Gemini Pro", core game  
	-- "GPT-5 mini", testing and infra
	-- "Claude Sonet4", core game
	-- "Grok", sound effects and HUD 

### background.mp3
Jazz 1
by Francisco Alvear

## Development Setup

1. Create and activate a virtual environment (recommended):

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
python -m venv .venv
.\.venv\Scripts\activate.bat

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
# Install runtime dependencies
python -m pip install -r requirements.txt

# (Optional) Install development dependencies (tests, build tools)
python -m pip install -r requirements-dev.txt
```

## Running the Game

You can run the game directly with Python (recommended when using the venv),
or with Pygame Zero's runner if you prefer.

Direct (run the game's main script):

```bash
# Ensure your virtualenv is activated (see Development Setup)
python main.py
```

Using Pygame Zero runner (alternative):

```bash
# preferred: uses the pgzrun script (installed by pgzero)
pgzrun main.py

# alternative if pgzrun isn't on PATH
python -m pgzero main.py
```

Controls

- Left / Right: rotate
- Up / Space: main thrust
- R: reset
- N: enter player name (before landing)
- Esc: quit
- C: credits

## Assets

The game includes the following assets in the `assets/` directory:

- `lander.png` - Lander sprite
- `icon.ico` - Application icon
- `background.ogg` or `background.mp3` - Background music (optional)

### Background Music

The game supports background music. Place an audio file named `background.ogg` or `background.mp3` in the `assets/` directory. The game will automatically load and play it in a loop at 30% volume.

Supported formats: OGG, MP3
If no music file is found, the game runs normally without music.

## Testing

The game includes a comprehensive test suite using pytest. To run the tests:

Run tests with coverage:
```bash
# Run all tests with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing

# Run tests with verbose output
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_persistence.py
```

### Test Structure

- `tests/test_input_handler.py` - Tests for keyboard input handling
- `tests/test_input_handler_extended.py` - Additional input tests (cursor, modifiers)
- `tests/test_persistence.py` - Tests for game state persistence (settings, scores)
- `tests/conftest.py` - Shared test fixtures and utilities

### Current Coverage

```
Name               Stmts   Miss  Cover
------------------------------------------
constants.py          7      0    100%
input_handler.py    125     22     82%
persistence.py       92     18     80%
```

Test coverage is focused on core game modules. The main game loop and rendering code have minimal coverage as they're tightly coupled to Pygame Zero.

### Running Tests During Development

During development, you can run tests continuously using pytest-watch:

```bash
# Run tests whenever files change
ptw
```

## Build & Release

Build a standalone executable (Windows, using PyInstaller via the project's helper):

```bash
# Make sure you have development dependencies installed
python -m pip install -r requirements-dev.txt

# Build both debug (console) and release (windowed) executables
python build.py

# Build and bundle VC runtime DLLs into dist/ (recommended for portability)
python build.py --bundle-vcruntime

# Built artifacts are written to the `dist/` folder
```

Notes on running built artifacts:

- Debug exe (prints console output):

```powershell
./dist/LunarLander-debug.exe
# or on Windows cmd
dist\LunarLander-debug.exe > game.log 2>&1
```

- Release exe (windowed, no console):

```powershell
./dist/LunarLander.exe
```

## Project TODO

This project TODO collects the actions, suggestions, and next steps from recent packaging and build work (PyInstaller, VC runtimes, NumPy removal). Use this checklist to track progress and run quick smoke-tests.

- [x] Restore stable build configuration
	- Restored `main` to commit `c07e507` which produced a working debug build.
- [x] Backup modified build files
	- Backed up experimental/temporary files to `backup/` before cleaning the working tree.
- [x] Build and smoke-test locally
	- Ran `python build.py` to produce `dist/LunarLander-debug.exe` and `dist/LunarLander.exe` and verified the debug exe prints expected messages.
- [x] Bundle minimal VC runtimes into `dist/`
	- Created a helper (`tools/bundle_vcruntime.py`) to copy `vcruntime140.dll` and `vcruntime140_1.dll` into `dist/` for improved portability.
- [x] Remove transient debug artifacts
	- Removed temporary files created during experimentation (DLL copies, helper scripts) from the working tree.
- [ ] Verify portability on a clean Windows VM
	- Test `dist/LunarLander.exe` on a clean machine. If missing DLL errors appear, either include the VC++ redistributable installer or add more CRT DLLs to `dist/`.
- [ ] Automate smoke test for release exe
	- Add a small CI/local script to run `dist/LunarLander.exe` for N seconds and check that it starts and exits cleanly.
- [ ] Decide permanent NumPy policy
	- Option A: Remove `numpy` from `requirements.txt` and uninstall it from the development environment (recommended if not used).  
	- Option B: Keep `numpy` but add a runtime hook to avoid the CPU dispatcher initialization problem (`NPY_DISABLE_CPU_FEATURES`), if you need numpy for other features.
- [ ] Improve build scripts
	- Keep `build.py` minimal and stable. Consider adding a `--bundle-vcruntime` option that runs the bundling helper after PyInstaller finishes.

Quick commands

```bash
# Build (uses PyInstaller via build.py)
python build.py

# Run debug exe (prints console output)
./dist/LunarLander-debug.exe

# Run release exe (windowed, no console)
./dist/LunarLander.exe

# Copy VC runtimes (example helper)
python tools/bundle_vcruntime.py --dist dist

# Optional: run release exe for 5 seconds then kill (Linux/WSL/bash example)
timeout 5s ./dist/LunarLander.exe || true
```

Notes

- The release build uses a windowed bootloader and typically doesn't produce console output. Use the debug build for log capture.
- For full portability to clean Windows systems, bundling only `vcruntime140*.dll` may or may not be sufficient — testing on a clean VM is the only reliable verification. If additional DLLs are required, include them explicitly or ship the official VC++ Redistributable installer.
- If you want, I can:
	- Add an automated smoke-test script and a small CI job.
	- Re-add or refine `tools/bundle_vcruntime.py` and expose a `--bundle-vcruntime` build flag.
	- Remove `numpy` from `requirements.txt` and optionally uninstall it from the dev environment.
