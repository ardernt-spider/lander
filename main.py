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
from pygame.constants import *
import pygame.font
from pgzero.keyboard import keyboard

# Make keyboard available globally
globals()['keyboard'] = keyboard

def load_high_score():
    try:
        if os.path.exists('scores.json'):
            with open('scores.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except Exception as e:
        print(f"Error loading high score: {e}")
    return 0

def save_high_score():
    try:
        with open('scores.json', 'w') as f:
            json.dump({'high_score': high_score}, f)
    except Exception as e:
        print(f"Error saving high score: {e}")

# Initialize Pygame
pygame.init()
pygame.font.init()

# Create game window
DISPLAY = pygame.display.set_mode((800, 600))
FONT = pygame.font.SysFont(None, 24)

WIDTH = 800
HEIGHT = 600

# Physics params
GRAVITY = 40.0           # pixels/s^2 downward
MAIN_THRUST = 160.0      # pixels/s^2 when main engine on
ROTATION_SPEED = 120.0   # degrees per second when rotating
SIDE_THRUST = 60.0       # lateral acceleration from side thrusters (not used separately)

# State
lander_pos = [WIDTH * 0.5, 100.0]
lander_vel = [0.0, 0.0]
lander_angle = 0.0  # degrees, 0 means pointing up
fuel = 100.0
alive = True
landed = False
crashed = False
score = 0
high_score = load_high_score()  # Load the high score from file
mission_start_time = 0
last_landing_stats = None  # To store stats of the last landing

# Landing pad
pad_width = 120
pad_height = 8
pad_x = random.randint(80, WIDTH - 80 - pad_width)
pad_y = HEIGHT - 40

# Visual sizes
lander_size = 18

# Frame timing
FPS = 60
DT = 1.0 / FPS

# HUD font sizes
TITLE = "Lunar Lander"


def reset():
    global lander_pos, lander_vel, lander_angle, fuel, alive, landed, crashed, pad_x, score, mission_start_time, last_landing_stats
    lander_pos = [WIDTH * 0.5, 100.0]
    lander_vel = [0.0, 0.0]
    lander_angle = 0.0
    fuel = 100.0
    alive = True
    landed = False
    crashed = False
    score = 0
    mission_start_time = pygame.time.get_ticks()
    last_landing_stats = None
    pad_x = random.randint(80, WIDTH - 80 - pad_width)


def apply_physics(dt):
    global lander_pos, lander_vel, lander_angle, fuel

    # Controls
    thrusting = keyboard.space or keyboard.up
    rotating_left = keyboard.left
    rotating_right = keyboard.right

    # Rotation
    if rotating_left and fuel > 0 and alive and not landed:
        lander_angle -= ROTATION_SPEED * dt
        fuel -= 0.02 * dt * FPS
    if rotating_right and fuel > 0 and alive and not landed:
        lander_angle += ROTATION_SPEED * dt
        fuel -= 0.02 * dt * FPS

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
        fuel -= 10.0 * dt
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
    global high_score, last_landing_stats
    
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
    
    # Update high score
    if total_score > high_score:
        high_score = total_score
        save_high_score()  # Save immediately when high score is beaten
    
    return total_score

def check_collision():
    global alive, landed, crashed, score
    # Simple collision with surface
    surface_y = HEIGHT - 40
    if lander_pos[1] + lander_size / 2 >= surface_y:
        # landed or crashed
        vx = lander_vel[0]
        vy = lander_vel[1]
        angle_ok = abs(lander_angle) < 15
        vel_ok = abs(vy) < 60 and abs(vx) < 60
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
            lander_sprite = pygame.image.load('assets/lander.png').convert_alpha()
            # Create a simple flame sprite
            flame_size = (32, 48)
            flame_sprite = pygame.Surface(flame_size, pygame.SRCALPHA)
            flame_points = [(16, 0), (32, 48), (0, 48)]
            pygame.draw.polygon(flame_sprite, (255, 120, 20), flame_points, 0)
        except FileNotFoundError:
            print("Error: Could not find lander.png in assets folder!")
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

    # Stars
    for i in range(40):
        # lightweight pseudo-random stars using pad_x as seed (stable per frame)
        sx = (i * 37 + pad_x) % WIDTH
        sy = (i * 53 + pad_x) % (HEIGHT - 200)
        DISPLAY.set_at((sx, sy), (255,255,255))

    # Moon surface
    surface_y = HEIGHT - 40
    pygame.draw.rect(DISPLAY, (80, 80, 80), pygame.Rect(0, surface_y, WIDTH, HEIGHT - surface_y))

    # Landing pad
    pygame.draw.rect(DISPLAY, (255, 255, 0), pygame.Rect(pad_x, pad_y, pad_width, pad_height))
    pygame.draw.rect(DISPLAY, (0, 0, 0), pygame.Rect(pad_x, pad_y, pad_width, pad_height), 1)

    # Lander
    draw_lander(DISPLAY)

    # HUD
    text = FONT.render(TITLE, True, (255, 255, 255))
    DISPLAY.blit(text, (10, 10))
    
    text = FONT.render(f"Fuel: {fuel:.0f}", True, (255, 255, 255))
    DISPLAY.blit(text, (10, 42))
    
    text = FONT.render(f"Pos: {lander_pos[0]:.0f}, {lander_pos[1]:.0f}", True, (255, 255, 255))
    DISPLAY.blit(text, (10, 66))
    
    text = FONT.render(f"Vel: {lander_vel[0]:.1f}, {lander_vel[1]:.1f}", True, (255, 255, 255))
    DISPLAY.blit(text, (10, 86))
    
    text = FONT.render(f"Angle: {lander_angle:.1f}°", True, (255, 255, 255))
    DISPLAY.blit(text, (10, 106))
    
    text = FONT.render(f"Pad X: {pad_x:.1f}", True, (255, 255, 255))
    DISPLAY.blit(text, (10, 126))

    # Show current score and high score
    if not landed and not crashed:
        # Show mission time during flight
        mission_time = (pygame.time.get_ticks() - mission_start_time) // 1000  # Convert to seconds
        text = FONT.render(f"Mission Time: {mission_time}s", True, (255, 255, 255))
        DISPLAY.blit(text, (WIDTH - 200, 10))

    text = FONT.render(f"High Score: {high_score}", True, (255, 255, 255))
    DISPLAY.blit(text, (WIDTH - 200, 34))

    if landed:
        # Main landing message
        text = FONT.render("LANDED! Press R to play again.", True, (0, 255, 0))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 80))
        DISPLAY.blit(text, text_rect)
        
        # Show landing statistics
        if last_landing_stats:
            stats = last_landing_stats
            y_pos = HEIGHT / 2 - 40
            stats_color = (200, 200, 100)
            
            texts = [
                f"Final Score: {stats['total']}",
                f"Base Score: {stats['base']}",
                f"Speed Bonus: {stats['speed']} (Landing speed: {stats['speed_value']:.1f})",
                f"Position Bonus: {stats['position']} (Off-center: {stats['distance']:.1f}px)",
                f"Fuel Bonus: {stats['fuel']} (Fuel left: {fuel:.0f})",
                f"Time Bonus: {stats['time']} (Mission time: {stats['mission_time']/1000:.1f}s)"
            ]
            
            for line in texts:
                text = FONT.render(line, True, stats_color)
                text_rect = text.get_rect(center=(WIDTH / 2, y_pos))
                DISPLAY.blit(text, text_rect)
                y_pos += 25
        
    if crashed:
        text = FONT.render("CRASHED! Press R to try again.", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        DISPLAY.blit(text, text_rect)
    
    # Update display
    pygame.display.flip()


def update():
    if keyboard.r:
        reset()
        return

    if not alive or landed:
        return

    apply_physics(DT)
    check_collision()


# Initialize random pad location at start
reset()
