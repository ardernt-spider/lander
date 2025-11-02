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
