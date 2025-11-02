"""
Simple Lunar Lander implemented for Pygame Zero.
Run with: pgzrun main.py

Controls:
- Left/Right arrows: rotate
- Up arrow / Space: main thrust

This is intentionally lightweight: no external assets, draws the lander as a polygon.
"""
import math
import random
import pygame
import json
import os
import sys
from pygame.constants import *
import pygame.font
from pgzero.keyboard import keyboard

# Make keyboard available globally
globals()['keyboard'] = keyboard

from datetime import datetime

# Helper to locate bundled resources (works with PyInstaller)
def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, works for development and PyInstaller bundles.

    Usage: resource_path('assets/lander.png')
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

MAX_TOP_SCORES = 10
DEFAULT_PLAYER_NAME = "Player"

# --- Persistent storage configuration ---
def get_data_dir():
    """Return a per-user data directory for the game and ensure it exists."""
    try:
        if os.name == 'nt':
            appdata = os.getenv('APPDATA') or os.path.expanduser('~')
            path = os.path.join(appdata, 'LunarLander')
        elif sys.platform == 'darwin':
            path = os.path.expanduser('~/Library/Application Support/LunarLander')
        else:
            path = os.path.expanduser('~/.local/share/lander')
        os.makedirs(path, exist_ok=True)
        return path
    except Exception:
        # Fallback to current directory
        return os.getcwd()

# Files inside the data directory
DATA_DIR = get_data_dir()
PLAYER_FILE = os.path.join(DATA_DIR, 'player.json')
SCORES_FILE = os.path.join(DATA_DIR, 'scores.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

# Default runtime settings (can be persisted in settings.json)
DEFAULT_SETTINGS = {
    'save_player': True,
    'save_scores': True,
}

def atomic_write_json(path, data):
    """Write JSON to a temp file and replace atomically."""
    try:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        # Fallback to non-atomic write
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return DEFAULT_SETTINGS.copy()
                s = DEFAULT_SETTINGS.copy()
                s.update(data)
                return s
    except Exception as e:
        print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        atomic_write_json(SETTINGS_FILE, settings)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Load runtime settings
_runtime_settings = load_settings()
SAVE_PLAYER = bool(_runtime_settings.get('save_player', True))
SAVE_SCORES = bool(_runtime_settings.get('save_scores', True))

def load_player_name():
    try:
        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get('name', DEFAULT_PLAYER_NAME)
    except Exception as e:
        print(f"Error loading player name: {e}")
    return DEFAULT_PLAYER_NAME

def save_player_name(name):
    if not SAVE_PLAYER:
        return
    try:
        atomic_write_json(PLAYER_FILE, {'name': name})
    except Exception as e:
        print(f"Error saving player name: {e}")

def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure backward compatibility
                if isinstance(data, dict) and 'high_score' in data:
                    # Convert old format to new format
                    return [{'score': data['high_score'],
                             'player': DEFAULT_PLAYER_NAME,
                             'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             'stats': None}]
                # Validate structure
                if isinstance(data, list):
                    valid = []
                    for item in data:
                        if isinstance(item, dict) and 'score' in item and 'player' in item and 'date' in item:
                            valid.append(item)
                    return valid
    except Exception as e:
        print(f"Error loading scores: {e}")
    return []

def save_new_score(score, stats):
    try:
        scores = load_scores()
        # Add new score with timestamp
        new_score = {
            'score': score,
            'player': current_player_name,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'stats': stats
        }
        scores.append(new_score)
        # Sort by score in descending order
        scores.sort(key=lambda x: x['score'], reverse=True)
        # Keep only top scores
        scores = scores[:MAX_TOP_SCORES]
        
        if SAVE_SCORES:
            atomic_write_json(SCORES_FILE, scores)
        return scores
    except Exception as e:
        print(f"Error saving score: {e}")
        return []

# Initialize Pygame
pygame.init()
pygame.font.init()

def get_screen_resolution():
    """Get the primary screen resolution in a cross-platform way."""
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            user32 = ctypes.windll.user32
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        elif os.name == 'posix':  # Linux and macOS
            try:
                # Try using Xrandr on Linux
                import subprocess
                output = subprocess.check_output('xrandr | grep "\\*"', shell=True).decode()
                resolution = output.split()[0]
                width, height = map(int, resolution.split('x'))
                return width, height
            except:
                # Fallback for macOS or if xrandr fails
                # Create a temporary window to get the real screen size
                temp_surface = pygame.display.set_mode((1, 1))
                info = pygame.display.Info()
                pygame.display.quit()
                pygame.display.init()
                return info.current_w, info.current_h
        else:
            # Fallback method
            temp_surface = pygame.display.set_mode((1, 1))
            info = pygame.display.Info()
            pygame.display.quit()
            pygame.display.init()
            return info.current_w, info.current_h
    except Exception as e:
        print(f"Warning: Could not detect screen resolution: {e}")
        # Return a safe default resolution
        return 1024, 768

# Get screen resolution
monitor_width, monitor_height = get_screen_resolution()
print(f"Detected screen resolution: {monitor_width}x{monitor_height}")

# Calculate 80% of screen size while maintaining aspect ratio
TARGET_RATIO = 4/3  # Standard game aspect ratio
scale = 0.8  # 80% of screen size

# Calculate width and height based on screen size while maintaining aspect ratio
if monitor_width / monitor_height > TARGET_RATIO:
    # Screen is wider than target ratio - limit by height
    HEIGHT = int(monitor_height * scale)
    WIDTH = int(HEIGHT * TARGET_RATIO)
else:
    # Screen is taller than target ratio - limit by width
    WIDTH = int(monitor_width * scale)
    HEIGHT = int(WIDTH / TARGET_RATIO)

# Create game window and center it
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont(None, int(HEIGHT * 24/600))  # Scale font size relative to screen height

# Scale factor for physics (relative to original 800x600 resolution)
SCALE_FACTOR = HEIGHT / 600.0

# Physics params (scaled with screen size)
GRAVITY = 40.0 * SCALE_FACTOR           # pixels/s^2 downward
MAIN_THRUST = 160.0 * SCALE_FACTOR      # pixels/s^2 when main engine on
ROTATION_SPEED = 120.0                  # degrees per second when rotating (no scaling needed)
SIDE_THRUST = 60.0 * SCALE_FACTOR       # lateral acceleration from side thrusters

# State
lander_pos = [WIDTH * 0.5, HEIGHT * 0.167]  # Start at 1/6 of screen height
lander_vel = [0.0, 0.0]
lander_angle = 0.0  # degrees, 0 means pointing up
fuel = 100.0
alive = True
landed = False
crashed = False
score = 0
top_scores = load_scores()  # Load all scores
mission_start_time = 0
last_landing_stats = None  # To store stats of the last landing

# Player name state
current_player_name = load_player_name()
entering_name = False
name_input = ""
name_input_time = 0  # For cursor blinking
show_name_cursor = True

# Key state for text input
key_input_time = 0
key_repeat_delay = 500  # ms before key starts repeating
key_repeat_interval = 50  # ms between repeated characters
# Per-key repeat tracking to avoid duplicate characters when holding keys
prev_pressed_keys = set()
key_last_time = {}        # last time a key produced input (ms)
key_next_repeat = {}     # next allowed repeat time (ms)

# Landing pad (scaled with screen size)
pad_width = int(120 * SCALE_FACTOR)
pad_height = int(8 * SCALE_FACTOR)
min_pad_margin = int(80 * SCALE_FACTOR)
pad_x = random.randint(min_pad_margin, WIDTH - min_pad_margin - pad_width)
pad_y = HEIGHT - int(40 * SCALE_FACTOR)

# Visual sizes
lander_size = int(18 * SCALE_FACTOR)

# Frame timing
TARGET_FPS = 60
MAX_DT = 1.0 / 30  # Cap the maximum time delta to prevent physics glitches
last_frame_time = 0
frame_times = []  # Keep track of recent frame times for FPS display
FPS_SAMPLE_SIZE = 30  # Number of frames to average for FPS calculation

# HUD font sizes
TITLE = "Lunar Lander"

def get_frame_time():
    global last_frame_time, frame_times
    current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
    
    if last_frame_time == 0:
        dt = 1.0 / TARGET_FPS
    else:
        dt = current_time - last_frame_time
        
    # Cap maximum dt to prevent physics glitches during lag spikes
    dt = min(dt, MAX_DT)
    
    # Update frame time tracking
    frame_times.append(dt)
    if len(frame_times) > FPS_SAMPLE_SIZE:
        frame_times.pop(0)
    
    last_frame_time = current_time
    return dt

def get_current_fps():
    if not frame_times:
        return TARGET_FPS
    avg_frame_time = sum(frame_times) / len(frame_times)
    return 1.0 / avg_frame_time if avg_frame_time > 0 else TARGET_FPS


def reset():
    global lander_pos, lander_vel, lander_angle, fuel, alive, landed, crashed, pad_x, score, mission_start_time, last_landing_stats
    lander_pos = [WIDTH * 0.5, HEIGHT * 0.167]  # Start at 1/6 of screen height
    lander_vel = [0.0, 0.0]
    lander_angle = 0.0
    fuel = 100.0
    alive = True
    landed = False
    crashed = False
    score = 0
    mission_start_time = pygame.time.get_ticks()
    last_landing_stats = None
    pad_x = random.randint(min_pad_margin, WIDTH - min_pad_margin - pad_width)


def apply_physics(dt):
    global lander_pos, lander_vel, lander_angle, fuel

    # Controls
    thrusting = keyboard.space or keyboard.up
    rotating_left = keyboard.left
    rotating_right = keyboard.right

    # Scale fuel consumption to maintain consistent rates regardless of frame rate
    BASE_ROTATION_FUEL_RATE = 1.2  # units per second
    BASE_THRUST_FUEL_RATE = 10.0   # units per second

    # Rotation
    if rotating_left and fuel > 0 and alive and not landed:
        lander_angle -= ROTATION_SPEED * dt
        fuel -= BASE_ROTATION_FUEL_RATE * dt
    if rotating_right and fuel > 0 and alive and not landed:
        lander_angle += ROTATION_SPEED * dt
        fuel -= BASE_ROTATION_FUEL_RATE * dt

    # Keep angle in [-180, 180]
    if lander_angle > 180:
        lander_angle -= 360
    if lander_angle < -180:
        lander_angle += 360

    # Thrust
    if thrusting and fuel > 0 and alive and not landed:
        # Convert angle to radians. In our coordinate system 0 deg = up (-y)
        rad = math.radians(lander_angle)
        # Thrust vector: angle 0 pushes up (negative y)
        ax = math.sin(rad) * MAIN_THRUST
        ay = -math.cos(rad) * MAIN_THRUST
        lander_vel[0] += ax * dt
        lander_vel[1] += ay * dt
        # consume fuel faster when thrusting
        fuel -= BASE_THRUST_FUEL_RATE * dt
        if fuel < 0:
            fuel = 0.0

    # Gravity
    lander_vel[1] += GRAVITY * dt

    # Integrate
    lander_pos[0] += lander_vel[0] * dt
    lander_pos[1] += lander_vel[1] * dt

    # Keep in horizontal bounds
    if lander_pos[0] < 0:
        lander_pos[0] = 0
        lander_vel[0] = 0
    if lander_pos[0] > WIDTH:
        lander_pos[0] = WIDTH
        lander_vel[0] = 0


def calculate_landing_score(vx, vy, landing_x, mission_time):
    global last_landing_stats
    
    # Base score for successful landing
    score = 1000

    # Speed bonus (better score for softer landing)
    speed = math.sqrt(vx*vx + vy*vy)
    speed_score = int(500 * (1.0 - min(1.0, speed/60.0)))
    
    # Position bonus (better score for landing closer to pad center)
    pad_center = pad_x + pad_width/2
    distance_from_center = abs(landing_x - pad_center)
    position_score = int(300 * (1.0 - min(1.0, distance_from_center/(pad_width/2))))
    
    # Fuel bonus
    fuel_score = int(fuel * 2)  # 2 points per unit of fuel remaining
    
    # Time bonus (faster landing = better score)
    time_score = int(1000 * min(1.0, 30000/max(1000, mission_time)))
    
    total_score = score + speed_score + position_score + fuel_score + time_score
    
    # Store landing stats
    last_landing_stats = {
        'total': total_score,
        'base': score,
        'speed': speed_score,
        'position': position_score,
        'fuel': fuel_score,
        'time': time_score,
        'speed_value': speed,
        'distance': distance_from_center,
        'mission_time': mission_time
    }
    
    # Save score and update top scores
    global top_scores
    top_scores = save_new_score(total_score, last_landing_stats)
    
    return total_score

def check_collision():
    global alive, landed, crashed, score
    # Simple collision with surface
    surface_y = HEIGHT - int(40 * SCALE_FACTOR)
    if lander_pos[1] + lander_size / 2 >= surface_y:
        # landed or crashed
        vx = lander_vel[0]
        vy = lander_vel[1]
        angle_ok = abs(lander_angle) < 15
        # Scale velocity limits with screen size
        max_safe_velocity = 60 * SCALE_FACTOR
        vel_ok = abs(vy) < max_safe_velocity and abs(vx) < max_safe_velocity
        over_pad = pad_x <= lander_pos[0] <= pad_x + pad_width

        if angle_ok and vel_ok and over_pad:
            landed = True
            alive = True
            # clamp position
            lander_pos[1] = surface_y - lander_size / 2
            lander_vel[0] = 0
            lander_vel[1] = 0
            # Calculate score
            mission_time = pygame.time.get_ticks() - mission_start_time
            score = calculate_landing_score(vx, vy, lander_pos[0], mission_time)
        else:
            crashed = True
            alive = False
            lander_vel[0] = 0
            lander_vel[1] = 0
            lander_pos[1] = surface_y - lander_size / 2
            score = 0  # No score for crashing


def draw_lander(surface):
    global lander_sprite, flame_sprite
    
    # Load sprites if not already loaded
    if 'lander_sprite' not in globals():
        try:
            lander_path = resource_path(os.path.join('assets', 'lander.png'))
            lander_sprite = pygame.image.load(lander_path).convert_alpha()
            # Create a simple flame sprite
            flame_size = (32, 48)
            flame_sprite = pygame.Surface(flame_size, pygame.SRCALPHA)
            flame_points = [(16, 0), (32, 48), (0, 48)]
            pygame.draw.polygon(flame_sprite, (255, 120, 20), flame_points, 0)
        except Exception as e:
            print(f"Error loading lander sprite from {lander_path}: {e}")
            return
    
    # Get the rect for positioning
    cx, cy = lander_pos
    sprite_rect = lander_sprite.get_rect()
    sprite_rect.center = (cx, cy)
    
    # Rotate the sprite
    rotated_lander = pygame.transform.rotate(lander_sprite, -lander_angle)  # Negative angle for clockwise rotation
    rotated_rect = rotated_lander.get_rect(center=sprite_rect.center)
    
    # Draw the lander
    surface.blit(rotated_lander, rotated_rect)
    
    # Draw flame if thrusting
    if (keyboard.space or keyboard.up) and fuel > 0 and alive and not landed:
        # Calculate flame position based on lander's angle
        rad = math.radians(lander_angle)
        offset = 20  # Distance from lander center to flame start
        
        # Calculate flame base position (at bottom of lander based on angle)
        flame_base_x = cx - math.sin(rad) * offset
        flame_base_y = cy + math.cos(rad) * offset
        
        # Create flame points relative to base position
        flame_length = 30 * (0.8 + random.random() * 0.4)  # Animated length
        flame_width = 16
        
        flame_points = [
            (flame_base_x, flame_base_y),  # Top point
            (flame_base_x - math.sin(rad - 0.5) * flame_width,  # Left point
             flame_base_y + math.cos(rad - 0.5) * flame_width),
            (flame_base_x - math.sin(rad) * flame_length,      # Bottom point
             flame_base_y + math.cos(rad) * flame_length),
            (flame_base_x - math.sin(rad + 0.5) * flame_width,  # Right point
             flame_base_y + math.cos(rad + 0.5) * flame_width),
        ]
        
        # Draw flame
        pygame.draw.polygon(surface, (255, 120, 20), flame_points, 0)


def draw():
    DISPLAY.fill((10, 10, 30))

    # Initialize star field if not exists
    if 'star_field' not in globals():
        global star_field
        star_field = []
        # Create three layers of stars for parallax effect
        for layer in range(3):
            layer_stars = []
            num_stars = 50 if layer == 0 else 30 if layer == 1 else 20
            for _ in range(num_stars):
                # Random position
                x = random.uniform(0, WIDTH)
                y = random.uniform(0, HEIGHT * 0.7)  # Only in upper 70% of screen
                # Random size (bigger in front layers)
                size = random.uniform(1, 2) if layer == 0 else \
                       random.uniform(1.5, 2.5) if layer == 1 else \
                       random.uniform(2, 3)
                # Random brightness
                brightness = random.uniform(0.5, 1.0)
                # Random color tint (slight blue/red variations)
                color_tint = random.choice([
                    (255, 255, 255),  # White
                    (255, 255, 220),  # Warm white
                    (220, 220, 255),  # Cool white
                    (255, 220, 220),  # Slight red
                    (240, 240, 255)   # Slight blue
                ])
                # Twinkle speed
                twinkle_speed = random.uniform(1, 3)
                layer_stars.append({
                    'x': x, 'y': y, 'size': size, 'brightness': brightness,
                    'color': color_tint, 'twinkle_speed': twinkle_speed,
                    'twinkle_offset': random.uniform(0, 6.28)  # Random phase
                })
            star_field.append(layer_stars)

    # Draw stars with parallax effect
    current_time = pygame.time.get_ticks() / 1000.0  # Time in seconds
    
    for layer, stars in enumerate(star_field):
        # Different parallax speeds for each layer
        parallax_speed = (0.2, 0.1, 0.05)[layer]
        frame_dt = 1.0 / TARGET_FPS  # Use target frame time for smooth movement
        dx = lander_vel[0] * parallax_speed * frame_dt
        
        for star in stars:
            # Update star position with parallax
            star['x'] = (star['x'] - dx) % WIDTH
            
            # Calculate twinkle effect
            twinkle = (math.sin(current_time * star['twinkle_speed'] + 
                              star['twinkle_offset']) + 1) * 0.5 * 0.3 + 0.7
            
            # Apply brightness and twinkle
            color = tuple(int(c * star['brightness'] * twinkle) for c in star['color'])
            
            # Draw star based on size
            if star['size'] <= 1:
                DISPLAY.set_at((int(star['x']), int(star['y'])), color)
            else:
                pygame.draw.circle(DISPLAY, color, 
                                (int(star['x']), int(star['y'])), 
                                star['size'] / 2)

    # Moon surface
    surface_y = HEIGHT - 40
    pygame.draw.rect(DISPLAY, (80, 80, 80), pygame.Rect(0, surface_y, WIDTH, HEIGHT - surface_y))

    # Landing pad
    pygame.draw.rect(DISPLAY, (255, 255, 0), pygame.Rect(pad_x, pad_y, pad_width, pad_height))
    pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(pad_x, pad_y, pad_width, pad_height), 1)

    # Lander
    draw_lander(DISPLAY)

    def draw_text_with_shadow(text, color, position, align="left"):
        shadow_offset = 1
        text_surface = FONT.render(text, True, (0, 0, 0))
        text_lit = FONT.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "right":
            text_rect.right = position[0]
            text_rect.top = position[1]
        elif align == "center":
            text_rect.centerx = position[0]
            text_rect.top = position[1]
        else:  # left
            text_rect.left = position[0]
            text_rect.top = position[1]
            
        # Draw shadow first
        shadow_rect = text_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        DISPLAY.blit(text_surface, shadow_rect)
        # Draw actual text
        DISPLAY.blit(text_lit, text_rect)
        
        return text_rect.bottom + 5  # Return bottom position for next line
        
    # Name input dialog
    if entering_name:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        DISPLAY.blit(overlay, (0, 0))
        
        # Draw input box
        input_y = HEIGHT * 0.4
        draw_text_with_shadow("Enter Your Name:", (200, 200, 200), (WIDTH/2, input_y), "center")
        input_text = name_input + ('_' if show_name_cursor else ' ')
        draw_text_with_shadow(input_text, (255, 255, 255), (WIDTH/2, input_y + 40), "center")
        draw_text_with_shadow("Press Enter to save, Esc to cancel", (150, 150, 150), (WIDTH/2, input_y + 80), "center")
    
    # HUD Layout
    left_margin = 10
    right_margin = WIDTH - 10
    y_pos = 10
    
    # Title
    y_pos = draw_text_with_shadow(TITLE, (255, 255, 255), (left_margin, y_pos))
    
    # Left panel - Flight Data
    fuel_color = (0, 255, 0) if fuel > 30 else (255, 255, 0) if fuel > 10 else (255, 0, 0)
    y_pos = draw_text_with_shadow(f"Fuel: {fuel:.0f}", fuel_color, (left_margin, y_pos))
    
    vel_magnitude = math.sqrt(lander_vel[0]**2 + lander_vel[1]**2)
    vel_color = (0, 255, 0) if vel_magnitude < 30 else (255, 255, 0) if vel_magnitude < 45 else (255, 0, 0)
    y_pos = draw_text_with_shadow(f"Velocity: {vel_magnitude:.1f}", vel_color, (left_margin, y_pos))
    
    angle_color = (0, 255, 0) if abs(lander_angle) < 10 else (255, 255, 0) if abs(lander_angle) < 25 else (255, 0, 0)
    y_pos = draw_text_with_shadow(f"Angle: {lander_angle:.1f}°", angle_color, (left_margin, y_pos))
    
    # Right panel - Score & Performance
    y_pos = 10
    if not landed and not crashed:
        # Player name and controls
        y_pos = draw_text_with_shadow(f"Pilot: {current_player_name}", (200, 200, 200), (right_margin, y_pos), "right")
        y_pos = draw_text_with_shadow("Press N to change name", (150, 150, 150), (right_margin, y_pos), "right")
        
        mission_time = (pygame.time.get_ticks() - mission_start_time) // 1000
        y_pos = draw_text_with_shadow(f"Mission Time: {mission_time}s", (200, 200, 200), (right_margin, y_pos), "right")
        
        current_fps = get_current_fps()
        fps_color = (0, 255, 0) if current_fps >= TARGET_FPS - 5 else \
                   (255, 255, 0) if current_fps >= TARGET_FPS - 15 else \
                   (255, 0, 0)
        y_pos = draw_text_with_shadow(f"FPS: {current_fps:.1f}", fps_color, (right_margin, y_pos), "right")
    
    # Top Scores - Compact display
    if top_scores:
        y_pos = draw_text_with_shadow("Best: ", (200, 200, 200), (right_margin, y_pos), "right")
        for i, score_data in enumerate(top_scores[:3]):
            score_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50)  # Gold, Silver, Bronze
            y_pos = draw_text_with_shadow(f"{score_data['score']}", score_color, (right_margin, y_pos), "right")

    if landed or crashed:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        DISPLAY.blit(overlay, (0, 0))
        
        y_pos = HEIGHT * 0.2
        
        if landed:
            # Landing message
            y_pos = draw_text_with_shadow("SUCCESSFUL LANDING!", (0, 255, 0), (WIDTH/2, y_pos), "center")
            y_pos = draw_text_with_shadow("Press R to play again", (200, 200, 200), (WIDTH/2, y_pos), "center")
            
            if last_landing_stats:
                stats = last_landing_stats
                y_pos += 20
                
                # Current landing summary
                total_color = (255, 215, 0)  # Gold color for total score
                y_pos = draw_text_with_shadow(f"FINAL SCORE: {stats['total']}", total_color, (WIDTH/2, y_pos), "center")
                y_pos += 10
                
                # Breakdown in columns
                col1_x = WIDTH/2 - 150
                col2_x = WIDTH/2 + 150
                row_y = y_pos
                
                # Left column
                draw_text_with_shadow(f"Landing Speed: {stats['speed_value']:.1f}", (200, 200, 100), (col1_x, row_y), "center")
                draw_text_with_shadow(f"Position Accuracy: {100 - (stats['distance']/(pad_width/2)*100):.0f}%", (200, 200, 100), (col2_x, row_y), "center")
                row_y += 30
                
                draw_text_with_shadow(f"Fuel Remaining: {fuel:.0f}", (200, 200, 100), (col1_x, row_y), "center")
                draw_text_with_shadow(f"Mission Time: {stats['mission_time']/1000:.1f}s", (200, 200, 100), (col2_x, row_y), "center")
                
                # Top Scores Table
                y_pos = row_y + 50
                draw_text_with_shadow("HALL OF FAME", (255, 255, 255), (WIDTH/2, y_pos), "center")
                y_pos += 30
                
                # Compact score table
                table_width = 400
                col_widths = [50, 100, 150, 100]  # Rank, Score, Date, Time
                x_start = WIDTH/2 - table_width/2
                
                # Headers
                headers = ["Rank", "Score", "Date", "Time"]
                x = x_start
                for header, width in zip(headers, col_widths):
                    draw_text_with_shadow(header, (150, 150, 150), (x + width/2, y_pos), "center")
                    x += width
                
                y_pos += 25
                
                # Score entries
                for i, score_data in enumerate(top_scores[:5]):
                    if i >= 5: break  # Show only top 5
                    
                    date_obj = datetime.strptime(score_data['date'], "%Y-%m-%d %H:%M:%S")
                    date_str = date_obj.strftime("%Y-%m-%d")
                    time_str = date_obj.strftime("%H:%M")
                    
                    # Highlight current score
                    row_color = (255, 215, 0) if score_data['score'] == stats['total'] else \
                              (192, 192, 192) if i == 0 else \
                              (150, 150, 150)
                    
                    x = x_start
                    cells = [f"#{i+1}", f"{score_data['score']}", date_str, time_str]
                    for cell, width in zip(cells, col_widths):
                        draw_text_with_shadow(cell, row_color, (x + width/2, y_pos), "center")
                        x += width
                    
                    y_pos += 25
        
        if crashed:
            y_pos = draw_text_with_shadow("CRASHED!", (255, 0, 0), (WIDTH/2, y_pos), "center")
            y_pos = draw_text_with_shadow("Press R to try again", (200, 200, 200), (WIDTH/2, y_pos), "center")
    
    # Update display
    pygame.display.flip()


def handle_text_input():
    global name_input, current_player_name, entering_name, key_input_time
    global prev_pressed_keys, key_last_time, key_next_repeat

    if not entering_name:
        return

    current_time = pygame.time.get_ticks()

    # Safe keyboard attribute checker that also consults pygame key state
    def key_pressed(k):
        pressed = False
        try:
            pressed = bool(getattr(keyboard, k.lower(), False))
        except Exception:
            pressed = False

        # Also check pygame key pressed state for robustness (numeric keypad, etc.)
        try:
            kp = pygame.key.get_pressed()
            # Map simple characters to pygame key constants
            keycode = None
            if len(k) == 1 and k.isalpha():
                keycode = getattr(pygame, f'K_{k}', None)
                if keycode is None:
                    keycode = getattr(pygame, f'K_{k.lower()}', None)
            elif len(k) == 1 and k.isdigit():
                keycode = getattr(pygame, f'K_{k}', None)
                if keycode is None:
                    keycode = getattr(pygame, f'K_KP{k}', None)
            elif k == ' ':
                keycode = pygame.K_SPACE
            elif k == '-':
                keycode = pygame.K_MINUS
            elif k == '_':
                keycode = pygame.K_MINUS

            if keycode is not None and kp[keycode]:
                pressed = True
        except Exception:
            pass

        return pressed

    # Handle confirm/cancel first
    if key_pressed('return') or keyboard.RETURN:
        if name_input.strip():  # Don't save empty names
            current_player_name = name_input.strip()
            save_player_name(current_player_name)
        entering_name = False
        name_input = ""
        # clear per-key state
        prev_pressed_keys.clear()
        return
    if key_pressed('escape') or keyboard.ESCAPE:
        entering_name = False
        name_input = ""
        prev_pressed_keys.clear()
        return

    # Allowed characters (lowercase). We'll append as typed (respecting Shift/CapsLock).
    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789 -_'

    # Modifier state for uppercase and shifted characters
    mods = 0
    try:
        mods = pygame.key.get_mods()
    except Exception:
        mods = 0
    shift_on = bool(mods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT | pygame.KMOD_SHIFT))
    caps_on = bool(mods & pygame.KMOD_CAPS)

    # Build set of currently pressed allowed characters
    pressed_chars = set(k for k in allowed_chars if key_pressed(k))
    backspace_now = key_pressed('backspace') or key_pressed('BACKSPACE') or keyboard.BACKSPACE

    # BACKSPACE handling with per-key timing
    if backspace_now:
        if 'BACKSPACE' not in prev_pressed_keys:
            # new press
            if name_input:
                name_input = name_input[:-1]
            key_last_time['BACKSPACE'] = current_time
            key_next_repeat['BACKSPACE'] = current_time + key_repeat_delay
        else:
            # held
            if current_time >= key_next_repeat.get('BACKSPACE', 0) and (
                current_time - key_last_time.get('BACKSPACE', 0) >= key_repeat_interval):
                if name_input:
                    name_input = name_input[:-1]
                key_last_time['BACKSPACE'] = current_time
                key_next_repeat['BACKSPACE'] = current_time + key_repeat_interval

    # Character input handling
    new_presses = pressed_chars - prev_pressed_keys
    held = pressed_chars & prev_pressed_keys

    # Process new presses immediately
    for ch in new_presses:
        if len(name_input) < 15:
            # Determine actual character considering Shift/CapsLock
            actual = ch
            if ch.isalpha():
                # Uppercase if shift xor caps
                if shift_on ^ caps_on:
                    actual = ch.upper()
            elif ch == '-':
                if shift_on:
                    actual = '_'
            # Append and track timing
            name_input += actual
            key_last_time[ch] = current_time
            key_next_repeat[ch] = current_time + key_repeat_delay
            # accept only one new char per frame to avoid flooding
            break

    # Process held keys for repeats
    if not new_presses:
        for ch in held:
            next_time = key_next_repeat.get(ch, 0)
            last_time = key_last_time.get(ch, 0)
            if current_time >= next_time and (current_time - last_time) >= key_repeat_interval:
                if len(name_input) < 15:
                    actual = ch
                    if ch.isalpha():
                        if shift_on ^ caps_on:
                            actual = ch.upper()
                    elif ch == '-':
                        if shift_on:
                            actual = '_'
                    name_input += actual
                    key_last_time[ch] = current_time
                    key_next_repeat[ch] = current_time + key_repeat_interval
                    break

    # Update prev_pressed_keys for next frame
    prev_pressed_keys = set(pressed_chars)

def update():
    global name_input_time, show_name_cursor, entering_name, name_input, prev_pressed_keys
    
    # Handle name input
    if entering_name:
        # Handle text input
        handle_text_input()
        
        # Blink cursor
        current_time = pygame.time.get_ticks()
        if current_time - name_input_time > 500:  # Blink every 500ms
            show_name_cursor = not show_name_cursor
            name_input_time = current_time
        return
    
    # Toggle name input with N key
    if keyboard.n and not (landed or crashed):
        entering_name = True
        name_input = current_player_name
        # Consume the initial 'n' press so it doesn't appear in the input.
        # Also initialize per-key timing so it isn't treated as a held key that repeats immediately.
        now = pygame.time.get_ticks()
        try:
            prev_pressed_keys.add('n')
        except Exception:
            prev_pressed_keys = set(['n'])
        key_last_time['n'] = now
        key_next_repeat['n'] = now + key_repeat_delay
        return
        
    if keyboard.r:
        reset()
        return

    if not alive or landed:
        return

    dt = get_frame_time()
    apply_physics(dt)
    check_collision()


# Initialize random pad location at start
reset()
