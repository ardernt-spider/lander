"""
Simple Lunar Lander game implemented in Pygame.
Run with: python main.py

Controls:
- Left/Right arrows: rotate
- Up arrow / Space: main thrust
- N: Edit player name
- R: Reset game
- Esc: Quit

This is intentionally lightweight: no external assets, draws the lander as a polygon.
"""
import math
import random
import pygame
import os
import sys
import pygame.font
# redundant: removed "from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE"
from pgzero.keyboard import keyboard
from datetime import datetime
from input_handler import TextInputHandler

# Import a small constants module (low-risk refactor)
from constants import (
    TARGET_RATIO,
    key_repeat_delay, key_repeat_interval, TARGET_FPS, TITLE
)

# Asset helpers
from assets import load_image, resource_path

# Persistence helpers
from persistence import (
    load_player_name, save_player_name, load_scores,
    save_new_score, SAVE_PLAYER
)

# Make keyboard available globally
globals()['keyboard'] = keyboard

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio

def load_background_music():
    """Load and start background music if available."""
    try:
        music_path = resource_path(os.path.join('assets', 'background.ogg'))  # Try OGG first
        if not os.path.exists(music_path):
            music_path = resource_path(os.path.join('assets', 'background.mp3'))  # Fallback to MP3
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            pygame.mixer.music.set_volume(0.3)  # Set volume to 30%
            print(f"Background music loaded: {music_path}")
        else:
            print("No background music file found (looked for background.ogg or background.mp3)")
    except Exception as e:
        print(f"Could not load background music: {e}")

# Load background music
load_background_music()

def load_crash_sound():
    """Load crash sound effect if available."""
    global crash_sound
    try:
        # Try different formats in order of preference
        sound_paths = [
            resource_path(os.path.join('assets', 'crash.wav')),
            resource_path(os.path.join('assets', 'crash.ogg')),
            resource_path(os.path.join('assets', 'crash.mp3'))
        ]
        for sound_path in sound_paths:
            if os.path.exists(sound_path):
                crash_sound = pygame.mixer.Sound(sound_path)
                crash_sound.set_volume(0.6)  # Set volume to 60%
                print(f"Crash sound loaded: {sound_path}")
                return
        print("No crash sound file found (looked for crash.wav, crash.ogg, or crash.mp3)")
        crash_sound = None
    except Exception as e:
        print(f"Could not load crash sound: {e}")
        crash_sound = None

# Load crash sound
crash_sound = None
thrust_sound = None
landing_sound = None
load_crash_sound()

def load_thrust_sound():
    """Load thrust sound effect if available."""
    global thrust_sound
    try:
        # Try different formats in order of preference
        sound_paths = [
            resource_path(os.path.join('assets', 'thrust.wav')),
            resource_path(os.path.join('assets', 'thrust.ogg')),
            resource_path(os.path.join('assets', 'thrust.mp3'))
        ]
        for sound_path in sound_paths:
            if os.path.exists(sound_path):
                thrust_sound = pygame.mixer.Sound(sound_path)
                thrust_sound.set_volume(0.4)  # Set volume to 40%
                print(f"Thrust sound loaded: {sound_path}")
                return
        print("No thrust sound file found (looked for thrust.wav, thrust.ogg, or thrust.mp3)")
        thrust_sound = None
    except Exception as e:
        print(f"Could not load thrust sound: {e}")
        thrust_sound = None

def load_landing_sound():
    """Load landing success sound effect if available."""
    global landing_sound
    try:
        # Try different formats in order of preference
        sound_paths = [
            resource_path(os.path.join('assets', 'landing.wav')),
            resource_path(os.path.join('assets', 'landing.ogg')),
            resource_path(os.path.join('assets', 'landing.mp3'))
        ]
        for sound_path in sound_paths:
            if os.path.exists(sound_path):
                landing_sound = pygame.mixer.Sound(sound_path)
                landing_sound.set_volume(0.8)  # Set volume to 80%
                print(f"Landing sound loaded: {sound_path}")
                return
        print("No landing sound file found (looked for landing.wav, landing.ogg, or landing.mp3)")
        landing_sound = None
    except Exception as e:
        print(f"Could not load landing sound: {e}")
        landing_sound = None

# Load thrust and landing sounds
thrust_sound = None
landing_sound = None
load_thrust_sound()
load_landing_sound()

pygame.font.init()

def get_screen_resolution() -> tuple[int, int]:
    """Get the primary screen resolution in a cross-platform way.
    
    Returns:
        tuple[int, int]: A tuple containing (width, height) of the primary screen in pixels
        
    This function attempts different methods based on the OS:
    - Windows: Uses GetSystemMetrics via ctypes
    - Linux: Tries xrandr command first
    - macOS/fallback: Uses pygame display info
    """
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
            except Exception:
                # Fallback for macOS or if xrandr fails
                # Create a temporary window to get the real screen size
                pygame.display.set_mode((1, 1))
                info = pygame.display.Info()
                pygame.display.quit()
                pygame.display.init()
                return info.current_w, info.current_h
        else:
            # Fallback method
            pygame.display.set_mode((1, 1))
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

# Sound state
thrust_playing = False

# Player name state
current_player_name = load_player_name()
# Text input handler (name editing)
text_input = TextInputHandler(repeat_delay=key_repeat_delay, repeat_interval=key_repeat_interval)

# Landing pad (scaled with screen size)
pad_width = int(120 * SCALE_FACTOR)
pad_height = int(8 * SCALE_FACTOR)
min_pad_margin = int(80 * SCALE_FACTOR)
pad_x = random.randint(min_pad_margin, WIDTH - min_pad_margin - pad_width)
pad_y = HEIGHT - int(40 * SCALE_FACTOR)

# Visual sizes
lander_size = int(18 * SCALE_FACTOR)

# Frame timing (TARGET_FPS provided by constants)
MAX_DT = 1.0 / 30  # Cap the maximum time delta to prevent physics glitches
last_frame_time = 0
frame_times = []  # Keep track of recent frame times for FPS display
FPS_SAMPLE_SIZE = 30  # Number of frames to average for FPS calculation

# HUD font sizes and title provided by constants

# UI Layout Constants
HUD_LEFT_MARGIN = int(WIDTH * 0.02)  # 2% of screen width
HUD_RIGHT_MARGIN = WIDTH - HUD_LEFT_MARGIN
HUD_TOP_MARGIN = int(HEIGHT * 0.02)  # 2% of screen height
HUD_BOTTOM_MARGIN = int(HEIGHT * 0.02)  # 2% of screen height
HUD_LINE_SPACING = int(HEIGHT * 0.03)  # 3% of screen height for line spacing
HUD_SECTION_SPACING = int(HEIGHT * 0.05)  # 5% for section spacing

# Table layout constants
TABLE_COLUMN_SPACING = int(WIDTH * 0.05)  # 5% of screen width
TABLE_ROW_SPACING = int(HEIGHT * 0.04)  # 4% of screen height

def get_frame_time() -> float:
    """Get the time since last frame, capped to prevent physics glitches.
    
    Returns:
        float: Time delta in seconds, capped at MAX_DT to prevent physics issues during lag.
        The first call returns 1/TARGET_FPS.
    """
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

def get_current_fps() -> float:
    """Calculate current FPS based on recent frame times.
    
    Returns:
        float: Current FPS averaged over recent frames. Returns TARGET_FPS
        if no frames have been processed yet or if time delta is zero.
    """
    if not frame_times:
        return TARGET_FPS
    avg_frame_time = sum(frame_times) / len(frame_times)
    return 1.0 / avg_frame_time if avg_frame_time > 0 else TARGET_FPS


def reset() -> None:
    """Reset the game state for a new attempt.
    
    Resets lander position, velocity, angle, fuel, landing pad location,
    and all game state flags (alive, landed, crashed). Also resets the
    mission timer and clears previous landing statistics.
    """
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
    # Restore background music volume to normal level
    pygame.mixer.music.set_volume(0.3)
    # Stop thrust sound if playing
    global thrust_playing
    if thrust_sound and thrust_playing:
        thrust_sound.stop()
        thrust_playing = False


def apply_physics(dt: float) -> None:
    """Update lander physics based on current controls and time delta.
    
    Args:
        dt: Time delta in seconds since last update.
        
    The function applies:
    - Rotation based on left/right controls
    - Main thrust vector based on angle when up/space is pressed
    - Constant gravity
    - Fuel consumption for thrusting and rotation
    - Position integration from velocity
    - Screen boundary checking
    """
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
        
        # Start thrust sound if not already playing
        global thrust_playing
        if thrust_sound and not thrust_playing:
            thrust_sound.play(-1)  # -1 means loop indefinitely
            thrust_playing = True
    else:
        # Stop thrust sound if it was playing
        if thrust_sound and thrust_playing:
            thrust_sound.stop()
            thrust_playing = False

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


def calculate_landing_score(vx: float, vy: float, landing_x: float, mission_time: int) -> int:
    """Calculate score for a successful landing based on various factors.
    
    Args:
        vx: Horizontal velocity at landing (pixels/second)
        vy: Vertical velocity at landing (pixels/second)
        landing_x: X coordinate where lander touched down
        mission_time: Total mission time in milliseconds
        
    Returns:
        int: Total score calculated from:
            - Base score (1000)
            - Speed bonus (up to 500)
            - Position bonus for landing near pad center (up to 300)
            - Fuel bonus (2 points per fuel unit)
            - Time bonus for quick landings (up to 1000)
            
    Side effects:
        Updates last_landing_stats global with detailed scoring breakdown
        Updates global score variable
        Saves score to persistent storage via save_new_score()
    """
    global last_landing_stats, score
    
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
    top_scores = save_new_score(total_score, last_landing_stats, current_player_name)
    
    return total_score

def check_collision() -> None:
    """Check for collision with surface and determine landing outcome.
    
    A successful landing requires:
    - Touching down on the landing pad
    - Vertical and horizontal velocity below maximum safe velocity
    - Lander angle within 15 degrees of vertical
    
    Side effects:
        Updates alive, landed, crashed state flags
        On successful landing: calculates and saves score
        On crash: zeros velocity and sets score to 0
    """
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
            # Play landing success sound if available
            if landing_sound:
                landing_sound.play()
        else:
            crashed = True
            alive = False
            lander_vel[0] = 0
            lander_vel[1] = 0
            lander_pos[1] = surface_y - lander_size / 2
            score = 0  # No score for crashing
            # Play crash sound if available
            if crash_sound:
                # Temporarily lower background music volume for crash sound
                original_music_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(0.1)  # Lower to 10%
                crash_sound.play()
                # Note: Music volume will be restored on next game reset


def draw_lander(surface: pygame.Surface) -> None:
    """Draw the lander sprite and optional thrust flame on the given surface.
    
    Args:
        surface: Pygame surface to draw on
        
    The lander sprite is loaded from assets/lander.png. When thrusting,
    a simple triangle flame effect is drawn behind the lander, rotated
    to match the lander's orientation. The flame size is randomly varied
    to create a flickering effect.
    
    Side effects:
        May create/update lander_sprite and flame_sprite globals on first call
        Logs an error if lander sprite cannot be loaded
    """
    global lander_sprite, flame_sprite

    # Prepare asset path (always defined for error reporting)
    lander_path = os.path.join('assets', 'lander.png')
    try:
        # Use central asset loader (handles PyInstaller bundles)
        lander_sprite = load_image(lander_path)
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
    sprite_rect.center = (int(cx), int(cy))
    
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


def draw() -> None:
    """Draw the complete game scene.
    
    Renders in order:
    1. Background with parallax star field
    2. Moon surface and landing pad
    3. Lander with thrust effects
    4. HUD with flight data, score, and player info
    5. Text overlays for name input and landing results
    
    The star field is created once and cached in a global;
    stars move with parallax based on lander velocity.
    """
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

    def draw_text_with_shadow(text: str, color: tuple[int, int, int], position: tuple[float | int, float | int], align: str = "left") -> int:
        """Draw text with a drop shadow for better legibility.
        
        Args:
            text: The text string to render
            color: RGB color tuple for the text
            position: (x, y) coordinates for text position (can be float or int)
            align: Text alignment - "left", "center", or "right" (default: "left")
            
        Returns:
            int: Y coordinate below the drawn text (useful for vertically stacking text)
            
        The text is drawn twice - once in black offset by 1 pixel for the shadow,
        then again in the specified color. The shadow helps text readability.
        """
        shadow_offset = 1
        text_surface = FONT.render(text, True, (0, 0, 0))
        text_lit = FONT.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # Convert position coordinates to integers
        x, y = int(position[0]), int(position[1])
        
        if align == "right":
            text_rect.right = x
            text_rect.top = y
        elif align == "center":
            text_rect.centerx = x
            text_rect.top = y
        else:  # left
            text_rect.left = x
            text_rect.top = y
            
        # Draw shadow first
        shadow_rect = text_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        DISPLAY.blit(text_surface, shadow_rect)
        # Draw actual text
        DISPLAY.blit(text_lit, text_rect)
        
        return text_rect.bottom + HUD_LINE_SPACING  # Use consistent line spacing
        
    # Name input dialog (delegated to TextInputHandler)
    if text_input.entering:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        DISPLAY.blit(overlay, (0, 0))

        # Draw input box
        input_y = HEIGHT * 0.4
        draw_text_with_shadow("Enter Your Name:", (200, 200, 200), (WIDTH/2, input_y), "center")
        input_text = text_input.get_display_text()
        draw_text_with_shadow(input_text, (255, 255, 255), (WIDTH/2, input_y + HUD_LINE_SPACING * 2), "center")
        draw_text_with_shadow("Press Enter to save, Esc to cancel", (150, 150, 150), (WIDTH/2, input_y + HUD_LINE_SPACING * 4), "center")
    
        draw_text_with_shadow("Press Enter to save, Esc to cancel", (150, 150, 150), (WIDTH/2, input_y + HUD_LINE_SPACING * 4), "center")
    
    # Credits display (always visible, small in bottom right)
    credits_x = WIDTH - HUD_LEFT_MARGIN
    credits_y = HEIGHT - HUD_BOTTOM_MARGIN
    small_font_size = int(HEIGHT * 16/600)  # Smaller font for credits
    small_font = pygame.font.SysFont(None, small_font_size)
    
    # Draw credits from bottom up
    credits_lines = [
        "\"Jazz 1\" by Francisco Alvear",
        "Grok, sound & HUD",
        "Claude Sonet, core game", 
        "GPT-5 mini, testing",
        "Gemini, core game"
    ]
    
    for i, line in enumerate(credits_lines):
        # Use small font for credits
        shadow_offset = 1
        text_surface = small_font.render(line, True, (0, 0, 0))
        text_lit = small_font.render(line, True, (150, 120, 120))
        text_rect = text_surface.get_rect()
        
        text_rect.right = credits_x
        text_rect.bottom = credits_y - i * int(small_font_size * 0.8)
        
        # Draw shadow first
        shadow_rect = text_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        DISPLAY.blit(text_surface, shadow_rect)
        # Draw actual text
        DISPLAY.blit(text_lit, text_rect)
    
    # HUD Layout
    left_margin = HUD_LEFT_MARGIN
    right_margin = HUD_RIGHT_MARGIN
    y_pos = HUD_TOP_MARGIN
    
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
    y_pos_right = HUD_TOP_MARGIN
    if not landed and not crashed:
        # Player name and controls
        y_pos_right = draw_text_with_shadow(f"Pilot: {current_player_name}", (200, 200, 200), (right_margin, y_pos_right), "right")
        y_pos_right = draw_text_with_shadow("Press N to change name", (150, 150, 150), (right_margin, y_pos_right), "right")
        
        mission_time = (pygame.time.get_ticks() - mission_start_time) // 1000
        y_pos_right = draw_text_with_shadow(f"Mission Time: {mission_time}s", (200, 200, 200), (right_margin, y_pos_right), "right")
        
        current_fps = get_current_fps()
        fps_color = (0, 255, 0) if current_fps >= TARGET_FPS - 5 else \
                   (255, 255, 0) if current_fps >= TARGET_FPS - 15 else \
                   (255, 0, 0)
        y_pos_right = draw_text_with_shadow(f"FPS: {current_fps:.1f}", fps_color, (right_margin, y_pos_right), "right")
    
    # Top Scores - Compact display
    if top_scores:
        y_pos_right = draw_text_with_shadow("Best: ", (200, 200, 200), (right_margin, y_pos_right), "right")
        for i, score_data in enumerate(top_scores[:3]):
            score_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50)  # Gold, Silver, Bronze
            player_name = score_data.get('player', 'Unknown')
            y_pos_right = draw_text_with_shadow(f"{score_data['score']} ({player_name})", score_color, (right_margin, y_pos_right), "right")

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
                y_pos += HUD_SECTION_SPACING
                
                # Current landing summary
                total_color = (255, 215, 0)  # Gold color for total score
                y_pos = draw_text_with_shadow(f"FINAL SCORE: {stats['total']}", total_color, (WIDTH/2, y_pos), "center")
                y_pos += HUD_SECTION_SPACING
                
                # Breakdown in columns
                col1_x = WIDTH/2 - 200
                col2_x = WIDTH/2 + 200
                row_y = y_pos
                
                # Left column
                draw_text_with_shadow(f"Landing Speed: {stats['speed_value']:.1f}", (200, 200, 100), (col1_x, row_y), "center")
                draw_text_with_shadow(f"Position Accuracy: {100 - (stats['distance']/(pad_width/2)*100):.0f}%", (200, 200, 100), (col2_x, row_y), "center")
                row_y += TABLE_ROW_SPACING
                
                draw_text_with_shadow(f"Fuel Remaining: {fuel:.0f}", (200, 200, 100), (col1_x, row_y), "center")
                draw_text_with_shadow(f"Mission Time: {stats['mission_time']/1000:.1f}s", (200, 200, 100), (col2_x, row_y), "center")
                
                # Top Scores Table
                y_pos = row_y + HUD_SECTION_SPACING
                draw_text_with_shadow("HALL OF FAME", (255, 255, 255), (WIDTH/2, y_pos), "center")
                y_pos += HUD_SECTION_SPACING
                
                # Compact score table
                table_width = min(600, WIDTH * 0.8)  # Responsive table width
                col_widths = [table_width * 0.12, table_width * 0.18, table_width * 0.25, table_width * 0.25, table_width * 0.2]  # Rank, Score, Player, Date, Time
                x_start = WIDTH/2 - table_width/2
                
                # Headers
                headers = ["Rank", "Score", "Player", "Date", "Time"]
                x = x_start
                for header, width in zip(headers, col_widths):
                    draw_text_with_shadow(header, (150, 150, 150), (x + width/2, y_pos), "center")
                    x += width
                
                y_pos += TABLE_ROW_SPACING
                
                # Score entries
                for i, score_data in enumerate(top_scores[:5]):
                    if i >= 5:
                        break  # Show only top 5
                    
                    date_obj = datetime.strptime(score_data['date'], "%Y-%m-%d %H:%M:%S")
                    date_str = date_obj.strftime("%Y-%m-%d")
                    time_str = date_obj.strftime("%H:%M")
                    player_name = score_data.get('player', 'Unknown')
                    
                    # Highlight current score
                    row_color = (255, 215, 0) if score_data['score'] == stats['total'] else \
                              (192, 192, 192) if i == 0 else \
                              (150, 150, 150)
                    
                    x = x_start
                    cells = [f"#{i+1}", f"{score_data['score']}", player_name, date_str, time_str]
                    for cell, width in zip(cells, col_widths):
                        draw_text_with_shadow(cell, row_color, (x + width/2, y_pos), "center")
                        x += width
                    
                    y_pos += TABLE_ROW_SPACING
        
        if crashed:
            y_pos = draw_text_with_shadow("CRASHED!", (255, 0, 0), (WIDTH/2, y_pos), "center")
            y_pos = draw_text_with_shadow("Press R to try again", (200, 200, 200), (WIDTH/2, y_pos), "center")
    
    # Update display
    pygame.display.flip()


# Text input is handled by TextInputHandler in input_handler.py

def update() -> None:
    """Update game state for the current frame.
    
    Handles:
    1. Name input mode (if active)
    2. Game reset via 'R' key
    3. Name edit mode toggle via 'N' key
    4. Physics simulation when game is active
    
    The function delegates text input handling to TextInputHandler
    and physics simulation to apply_physics().
    """
    global current_player_name

    # If name editing is active, let TextInputHandler process input
    if text_input.entering:
        status, name = text_input.update(keyboard)
        if status == 'commit':
            if name:
                current_player_name = name
                if SAVE_PLAYER:
                    save_player_name(current_player_name)
        # cancel or idle simply return to game
        return

    # Toggle name input with N key
    if keyboard.n and not (landed or crashed):
        # start input and consume the initial 'n' press so it doesn't appear
        text_input.start(current_player_name, consume_keys={'n'})
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

def main() -> None:
    """Main entry point for the game. Runs the game loop.
    
    Sets up the game clock and runs the main game loop handling:
    - Event processing (quit, keyboard)
    - Game state updates
    - Drawing
    - Frame rate control
    """
    global clock, DISPLAY
    
    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Debug info
    print(f"Debug: Window size = {WIDTH}x{HEIGHT}")
    print(f"Debug: Lander position = {lander_pos}")
    print("Debug: Game starting...")

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Update keyboard state for Pygame Zero compatibility
                keyboard._press(event.key)
            elif event.type == pygame.KEYUP:
                # Update keyboard state for Pygame Zero compatibility
                keyboard._release(event.key)

        # Run game logic
        update()
        
        # Draw everything
        draw()
        
        # Control frame rate
        clock.tick(TARGET_FPS)

    # Clean up
    pygame.mixer.music.stop()  # Stop background music
    pygame.quit()

if __name__ == '__main__':
    main()
