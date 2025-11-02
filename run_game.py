"""
Entry point wrapper for the PyInstaller executable.
Directly imports all game functions and variables from main.py,
then starts the game loop.
"""
import pygame
from pygame.locals import *
from pgzero.keyboard import keyboard

# Make keyboard available globally
globals()['keyboard'] = keyboard

from main import (
    # Constants
    WIDTH, HEIGHT, GRAVITY, MAIN_THRUST, ROTATION_SPEED,
    SIDE_THRUST, FPS, DT, TITLE,
    # Game state
    lander_pos, lander_vel, lander_angle, fuel, alive,
    landed, crashed, pad_width, pad_height, pad_x, pad_y,
    lander_size,
    # Functions
    reset, apply_physics, check_collision, draw_lander,
    draw, update
)

print("Debug: Game functions imported")
print(f"Debug: Window size = {WIDTH}x{HEIGHT}")
print(f"Debug: Lander position = {lander_pos}")

# Initialize Pygame
pygame.init()

# Create clock for controlling frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            # Update keyboard state for Pygame Zero compatibility
            keyboard._press(event.key)
        elif event.type == KEYUP:
            # Update keyboard state for Pygame Zero compatibility
            keyboard._release(event.key)

    # Run game logic
    update()
    
    # Draw everything
    draw()
    
    # Control frame rate
    clock.tick(FPS)

# Clean up
pygame.quit()