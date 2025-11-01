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
import pgzero
import pgzrun
import pygame

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
    global lander_pos, lander_vel, lander_angle, fuel, alive, landed, crashed, pad_x
    lander_pos = [WIDTH * 0.5, 100.0]
    lander_vel = [0.0, 0.0]
    lander_angle = 0.0
    fuel = 100.0
    alive = True
    landed = False
    crashed = False
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


def check_collision():
    global alive, landed, crashed
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
        else:
            crashed = True
            alive = False
            lander_vel[0] = 0
            lander_vel[1] = 0
            lander_pos[1] = surface_y - lander_size / 2


def draw_lander(surface):
    # draw a simple triangular lander centered at lander_pos, rotated by lander_angle
    cx, cy = lander_pos
    size = lander_size
    # base triangle pointing up (0 deg)
    pts = [(-size * 0.6, size * 0.8), (0, -size), (size * 0.6, size * 0.8)]
    rad = math.radians(lander_angle)
    cosr = math.cos(rad)
    sinr = math.sin(rad)
    rot_pts = []
    for x, y in pts:
        rx = x * cosr - y * sinr
        ry = x * sinr + y * cosr
        rot_pts.append((cx + rx, cy + ry))

    #screen.draw.filled_polygon(rot_pts, 'white')
    #screen.draw.polygon(rot_pts, 'black')
    #pygame.draw.polygon(screen.surface, (255, 255, 255), rot_pts, 1)
    pygame.draw.polygon(screen.surface, (0, 128, 255), rot_pts, 5)

    # fuel flame if thrusting
    if (keyboard.space or keyboard.up) and fuel > 0 and alive and not landed:
        # flame points
        flame_pts = [(-6, size * 0.8 + 6), (0, size * 1.6 + random.uniform(-6, 6)), (6, size * 0.8 + 6)]
        rot_flame = []
        for x, y in flame_pts:
            rx = x * cosr - y * sinr
            ry = x * sinr + y * cosr
            rot_flame.append((cx + rx, cy + ry))
        #screen.draw.filled_polygon(rot_flame, (255, 120, 20))
        pygame.draw.polygon(screen.surface, (255, 0, 0), rot_flame, 5)


def draw():
    screen.fill((10, 10, 30))

    # Stars
    for i in range(40):
        # lightweight pseudo-random stars using pad_x as seed (stable per frame)
        sx = (i * 37 + pad_x) % WIDTH
        sy = (i * 53 + pad_x) % (HEIGHT - 200)
        # screen.draw.pixel((sx, sy), 'white')
        screen.surface.set_at((sx, sy), (255,255,255))

    # Moon surface
    surface_y = HEIGHT - 40
    screen.draw.filled_rect(Rect((0, surface_y), (WIDTH, HEIGHT - surface_y)), (80, 80, 80))

    # Landing pad
    screen.draw.filled_rect(Rect((pad_x, pad_y), (pad_width, pad_height)), 'yellow')
    screen.draw.rect(Rect((pad_x, pad_y), (pad_width, pad_height)), 'black')

    # Lander
    draw_lander(screen)

    # HUD
    screen.draw.text(TITLE, (10, 10), fontsize=28, color='white')
    screen.draw.text(f"Fuel: {fuel:.0f}", (10, 42), fontsize=20, color='white')
    screen.draw.text(f"Pos: {lander_pos[0]:.0f}, {lander_pos[1]:.0f}", (10, 66), fontsize=16, color='white')
    screen.draw.text(f"Vel: {lander_vel[0]:.1f}, {lander_vel[1]:.1f}", (10, 86), fontsize=16, color='white')
    screen.draw.text(f"Angle: {lander_angle:.1f}\u00B0", (10, 106), fontsize=16, color='white')
    screen.draw.text(f"Pad X: {pad_x:.1f}\u00B0", (10, 126), fontsize=16, color='white')


    if landed:
        screen.draw.text("LANDED! Press R to play again.", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color='lime')
    if crashed:
        screen.draw.text("CRASHED! Press R to try again.", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color='red')


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
