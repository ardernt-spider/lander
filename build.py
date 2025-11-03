"""
Build script for creating a Windows executable of the Lunar Lander game.
Run with: python build.py

This script uses PyInstaller to create either a debug version (with console)
or a release version (without console) of the game. Both versions will be
created by default when running the script.
"""
import PyInstaller.__main__
import os
import shutil
import pgzero
import sys
import subprocess
import argparse

# Get paths for required resources
PGZERO_PATH = os.path.dirname(pgzero.__file__)
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico'))
ASSETS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

def build_game(debug=False):
    """Build a version of the game executable.
    
    Args:
        debug: If True, builds with console window and debug name
    """
    # Set name and console mode based on debug flag
    name = 'LunarLander-debug' if debug else 'LunarLander'
    windowed = not debug  # Show console in debug mode
    
    # PyInstaller configuration
    cmd = [
        'main.py',                          # Main game script
        f'--name={name}',                   # Executable name
        '--onefile',                        # Create single executable
        f'--add-data={PGZERO_PATH};pgzero', # Include pgzero data
        f'--add-data={ASSETS_PATH};assets',  # Include game assets
        '--hidden-import=pgzero.builtins',   # Required imports
        '--hidden-import=pygame',
        '--hidden-import=pygame.base',
        '--collect-all=pgzero',             # Get all pgzero resources
        f'--icon={ICON_PATH}'               # Custom icon
    ]
    
    # Add windowed flag for release builds
    if windowed:
        cmd.append('--windowed')

    
    # Run PyInstaller with our configuration
    PyInstaller.__main__.run(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build the Lunar Lander executables')
    parser.add_argument('--bundle-vcruntime', action='store_true',
                        help='After building, copy VC runtime DLLs into each dist/ folder')
    args = parser.parse_args()

    # Clean old builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    print("Building debug version...")
    build_game(debug=True)
    print("\nBuilding release version...")
    build_game(debug=False)
    print("\nBuild complete! Executables are in the 'dist' folder.")

    # Optionally bundle VC runtime DLLs into dist/
    if args.bundle_vcruntime:
        # Call the bundling helper script.
        bundler = os.path.join(os.path.dirname(__file__), 'tools', 'bundle_vcruntime.py')
        if os.path.exists(bundler):
            print('\nBundling VC runtime DLLs into dist/...')
            try:
                subprocess.check_call([sys.executable, bundler, '--dist', 'dist'])
            except subprocess.CalledProcessError:
                print('Bundling helper failed (non-zero exit)')
        else:
            print(f'Bundling helper not found: {bundler}')