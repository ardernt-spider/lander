"""
Create a simple icon for the Lunar Lander game.
This script generates a basic geometric icon representing a lunar lander.
"""
from PIL import Image, ImageDraw
import os

def draw_lander(image, draw, center_x, center_y, with_background=False):
    """Draw the lander on the given image."""
    if with_background:
        # Draw stars
        for i in range(20):
            x = (i * 37) % image.width
            y = (i * 53) % (image.height - 100)
            draw.point((x, y), fill=(255, 255, 255))
        
        # Draw moon surface
        surface_y = image.height - 40
        draw.rectangle([(0, surface_y), (image.width, image.height)], 
                      fill=(80, 80, 80))
        
        # Draw landing pad
        pad_width = 60
        pad_x = image.width // 2 - pad_width // 2
        pad_y = surface_y - 10
        draw.rectangle([(pad_x, pad_y), (pad_x + pad_width, pad_y + 10)], 
                      fill=(255, 255, 0), outline=(0, 0, 0))

    # Main body (capsule)
    capsule_points = [
        (center_x, center_y - 40),       # Top
        (center_x - 35, center_y + 20),  # Bottom left
        (center_x + 35, center_y + 20)   # Bottom right
    ]
    # Draw filled white capsule with black outline
    draw.polygon(capsule_points, fill=(255, 255, 255), outline=(0, 0, 0))
    
    # Landing legs with pads
    # Left leg
    draw.line([(center_x - 25, center_y + 15), 
               (center_x - 40, center_y + 45)], 
              fill=(128, 128, 128), width=3)
    draw.line([(center_x - 47, center_y + 45),
               (center_x - 33, center_y + 45)],
              fill=(192, 192, 192), width=3)
              
    # Right leg
    draw.line([(center_x + 25, center_y + 15),
               (center_x + 40, center_y + 45)],
              fill=(128, 128, 128), width=3)
    draw.line([(center_x + 47, center_y + 45),
               (center_x + 33, center_y + 45)],
              fill=(192, 192, 192), width=3)

def create_icon():
    # Create window icon with background
    size = 256
    # Use RGB for ICO file
    icon_image = Image.new('RGB', (size, size), (10, 10, 30))
    icon_draw = ImageDraw.Draw(icon_image)
    
    # Draw lander with background for window icon
    draw_lander(icon_image, icon_draw, size//2, size//2, with_background=True)
    
    # Create sprite without background
    sprite_size = 128
    sprite_image = Image.new('RGBA', (sprite_size, sprite_size), (0, 0, 0, 0))
    sprite_draw = ImageDraw.Draw(sprite_image)
    
    # Draw just the lander for the sprite
    draw_lander(sprite_image, sprite_draw, sprite_size//2, sprite_size//2, with_background=False)
    
    # Ensure the assets directory exists
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Ensure the assets directory exists
    if not os.path.exists('assets'):
        os.makedirs('assets')

    # Save window icon with multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    icon_images = []
    for s in icon_sizes:
        # Resize and convert to RGB for each size
        icon_images.append(icon_image.resize(s, Image.Resampling.LANCZOS).convert('RGB'))

    # Save the icon with multiple sizes
    icon_path = os.path.join('assets', 'icon.ico')
    icon_images[0].save(icon_path, format='ICO', sizes=icon_sizes)
    print(f"Icon created at: {icon_path}")
    
    # Save the sprite for the game
    game_sprite_size = (64, 64)  # Size for the game sprite
    game_sprite = sprite_image.resize(game_sprite_size, Image.Resampling.LANCZOS)
    game_sprite_path = os.path.join('assets', 'lander.png')
    game_sprite.save(game_sprite_path, format='PNG')
    print(f"Game sprite created at: {game_sprite_path}")

if __name__ == '__main__':
    create_icon()