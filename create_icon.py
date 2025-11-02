"""
Create a simple icon for the Lunar Lander game.
This script generates a basic geometric icon representing a lunar lander.
"""
from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a new image with a dark blue background
    size = 256
    # Use RGB (no alpha) to encourage PIL to write multiple bitmap ICO sizes
    image = Image.new('RGB', (size, size), (10, 10, 30))
    draw = ImageDraw.Draw(image)
    
    # Draw stars
    for i in range(20):
        x = (i * 37) % size
        y = (i * 53) % (size - 100)
        draw.point((x, y), fill=(255, 255, 255))
    
    # Draw moon surface
    surface_y = size - 40
    draw.rectangle([(0, surface_y), (size, size)], fill=(80, 80, 80))
    
    # Draw landing pad
    pad_width = 60
    pad_x = size // 2 - pad_width // 2
    pad_y = surface_y - 10
    draw.rectangle([(pad_x, pad_y), (pad_x + pad_width, pad_y + 10)], 
                  fill=(255, 255, 0), outline=(0, 0, 0))
    
    # Draw the lander
    center_x = size // 2
    center_y = size // 2
    
    # Main body (capsule)
    capsule_points = [
        (center_x, center_y - 40),       # Top
        (center_x - 35, center_y + 20),  # Bottom left
        (center_x + 35, center_y + 20)   # Bottom right
    ]
    # Draw filled white capsule with black outline
    draw.polygon(capsule_points, fill=(255, 255, 255), outline=(0, 0, 0))
    
    # Landing legs with pads
    leg_length = 30
    pad_width = 15
    
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
    
    # Add thruster flames (red-orange gradient)
    flame_points = [
        (center_x - 10, center_y + 20),      # Left base
        (center_x + 10, center_y + 20),      # Right base
        (center_x, center_y + 40)            # Bottom point
    ]
    draw.polygon(flame_points, fill=(255, 100, 0), outline=(255, 50, 0))
    
    # Ensure the assets directory exists
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Save as .ico file with multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    icon_images = []
    for s in icon_sizes:
        # Resize and convert to RGB for each size
        icon_images.append(image.resize(s, Image.Resampling.LANCZOS).convert('RGB'))

    # Save the icon with multiple sizes (ensure RGB/BMP entries)
    icon_path = os.path.join('assets', 'icon.ico')
    icon_images[0].save(icon_path, format='ICO', sizes=icon_sizes)
    print(f"Icon created at: {icon_path}")

if __name__ == '__main__':
    create_icon()