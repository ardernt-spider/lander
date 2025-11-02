"""
Build script for creating a Windows executable of the Lunar Lander game.
Run with: python build.py
"""
import PyInstaller.__main__
import os
import shutil
import pgzero
import sys

# Get pgzero package location
PGZERO_PATH = os.path.dirname(pgzero.__file__)
# Absolute path to custom icon so PyInstaller picks it up reliably
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico'))

def build_game(debug=False):
    # Clean previous builds if not building debug version
    if not debug:
        for dir_name in ['build', 'dist']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
    
    # Set name and console flag based on debug mode
    name = 'LunarLander-debug' if debug else 'LunarLander'
    console_flag = [] if debug else ['--windowed']
    
    # Get pgzero package location
    pgzero_path = os.path.dirname(pgzero.__file__)
    
    # PyInstaller configuration
    cmd = [
        'run_game.py',               # Our wrapper script
        f'--name={name}',            # Name of the executable
        '--onefile',                 # Create a single executable
        f'--add-data={pgzero_path};pgzero',  # Include pgzero package data
        '--hidden-import=pgzero.builtins',   # Required for pgzero
        '--hidden-import=pygame',            # Ensure pygame is included
        '--hidden-import=pygame.base',       # Additional pygame components
        '--collect-all=pgzero',             # Get all pgzero resources
        f'--icon={ICON_PATH}'                # Custom icon (absolute path)
    ]
    
    # Add windowed flag for non-debug builds
    if not debug:
        cmd.append('--windowed')
    
    PyInstaller.__main__.run(cmd)

def build_debug():
    """Build the debug version with console window"""
    cmd = [
        'run_game.py',                      # Our wrapper script
        '--name=LunarLander-debug',         # Name of the executable
        '--onefile',                        # Create a single executable
        f'--add-data={PGZERO_PATH};pgzero',  # Include pgzero package data
        '--hidden-import=pgzero.builtins',  # Required for pgzero
        '--hidden-import=pygame',           # Ensure pygame is included
        '--hidden-import=pygame.base',      # Additional pygame components
        '--collect-all=pgzero'             # Get all pgzero resources
    ]
    PyInstaller.__main__.run(cmd)

def build_release():
    """Build the release version without console window"""
    cmd = [
        'run_game.py',                      # Our wrapper script
        '--name=LunarLander',              # Name of the executable
        '--onefile',                        # Create a single executable
        '--windowed',                       # Hide console window
        f'--add-data={PGZERO_PATH};pgzero',  # Include pgzero package data
        '--hidden-import=pgzero.builtins',  # Required for pgzero
        '--hidden-import=pygame',           # Ensure pygame is included
        '--hidden-import=pygame.base',      # Additional pygame components
        '--collect-all=pgzero'             # Get all pgzero resources
    ]
    PyInstaller.__main__.run(cmd)

if __name__ == '__main__':
    # Clean old builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    print("Building debug version...")
    build_debug()
    print("\nBuilding release version...")
    build_release()
    print("\nBuild complete! Executables are in the 'dist' folder:")