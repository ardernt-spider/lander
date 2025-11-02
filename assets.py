"""Asset helpers: resource path resolution and simple loaders.

This centralises logic for locating bundled resources (works with PyInstaller)
and caches loaded images.
"""
import os
import sys
import pygame

_image_cache = {}

def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, works for dev and PyInstaller bundles.

    Example: resource_path('assets/lander.png')
    """
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_image(relative_path: str) -> pygame.Surface:
    """Load and cache an image by relative path.

    Raises the underlying pygame error if the file cannot be loaded.
    """
    if relative_path in _image_cache:
        return _image_cache[relative_path]

    full = resource_path(relative_path)
    surf = pygame.image.load(full).convert_alpha()
    _image_cache[relative_path] = surf
    return surf
