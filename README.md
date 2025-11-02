# Lunar Lander (Pygame Zero)

A small Lunar Lander clone implemented using Pygame Zero. The game draws the lander procedurally (no external assets).

Requirements

- Python 3.8+
- Pygame Zero (install with pip)

## Development Setup

1. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
# Install runtime dependencies
python -m pip install -r requirements.txt

# Install development dependencies (tests, build tools)
python -m pip install -r requirements-dev.txt
```

## Running the Game

```bash
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

Build a standalone executable:

```bash
# Make sure you have development dependencies installed
python -m pip install -r requirements-dev.txt
# run the build helper (uses PyInstaller via build.py)
python .\build.py
# built artifacts are written to the `dist\` folder
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
