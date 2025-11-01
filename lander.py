# Game window dimensions
WIDTH = 800
HEIGHT = 600

# Load a player image (make sure 'player.png' is in the same folder)
player = Actor('player')
player.pos = WIDTH // 2, HEIGHT // 2

# Movement speed
speed = 5

def draw():
    screen.clear()
    screen.fill((0, 0, 30))  # Dark background
    player.draw()

def update():
    if keyboard.left:
        player.x -= speed
    if keyboard.right:
        player.x += speed
    if keyboard.up:
        player.y -= speed
    if keyboard.down:
        player.y += speed

# Required to run with `py lander.py`
import pgzrun
pgzrun.go()