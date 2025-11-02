"""Small constants module extracted from main.py for easier refactor.

Keep this very minimal to avoid import cycles. Only contains static constants.
"""
MAX_TOP_SCORES = 10
DEFAULT_PLAYER_NAME = "Player"

# Display / layout
TARGET_RATIO = 4/3  # Standard game aspect ratio
TITLE = "Lunar Lander"

# Timing
TARGET_FPS = 60

# Input repeat defaults (milliseconds)
key_repeat_delay = 500  # ms before key starts repeating
key_repeat_interval = 50  # ms between repeated characters
