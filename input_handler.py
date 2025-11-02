"""Input handling helpers for text input (name editing) with per-key repeat.

This module encapsulates the previous ad-hoc text input logic from main.py so
it can be tested and reasoned about separately.
"""
from typing import Optional, Tuple
import pygame


class TextInputHandler:
    def __init__(self, repeat_delay: int = 500, repeat_interval: int = 50, max_length: int = 15):
        self.repeat_delay = repeat_delay
        self.repeat_interval = repeat_interval
        self.max_length = max_length

        self.entering = False
        self.name = ""
        self.name_time = 0
        self.show_cursor = True

        # per-key repeat state
        self.prev_pressed_keys = set()
        self.key_last_time = {}
        self.key_next_repeat = {}

    def start(self, initial_name: str = "", consume_keys: Optional[set] = None) -> None:
        self.entering = True
        self.name = initial_name or ""
        self.name_time = pygame.time.get_ticks()
        self.show_cursor = True
        self.prev_pressed_keys = set(consume_keys) if consume_keys else set()
        now = pygame.time.get_ticks()
        for k in (consume_keys or []):
            self.key_last_time[k] = now
            self.key_next_repeat[k] = now + self.repeat_delay

    def stop(self) -> None:
        self.entering = False
        self.prev_pressed_keys.clear()
        self.key_last_time.clear()
        self.key_next_repeat.clear()
        self.name_time = 0
        self.show_cursor = True

    def get_display_text(self) -> str:
        return self.name + ('_' if self.show_cursor else ' ')

    def _key_pressed(self, keyboard, k: str) -> bool:
        # Safe getter for pgzero keyboard plus pygame fallback
        pressed = False
        try:
            pressed = bool(getattr(keyboard, k.lower(), False))
        except Exception:
            pressed = False

        try:
            kp = pygame.key.get_pressed()
            keycode = None
            if len(k) == 1 and k.isalpha():
                keycode = getattr(pygame, f'K_{k.lower()}', None)
            elif len(k) == 1 and k.isdigit():
                keycode = getattr(pygame, f'K_{k}', None) or getattr(pygame, f'K_KP{k}', None)
            elif k == ' ':
                keycode = pygame.K_SPACE
            elif k in ('-', '_'):
                keycode = pygame.K_MINUS

            if keycode is not None and kp[keycode]:
                pressed = True
        except Exception:
            pass

        return pressed

    def update(self, keyboard) -> Tuple[str, Optional[str]]:
        """Process input. Returns (status, name).

        status is one of: 'idle', 'commit', 'cancel'. When commit, name is the final name.
        """
        if not self.entering:
            return 'idle', None

        current_time = pygame.time.get_ticks()

        # Blink cursor
        if current_time - self.name_time > 500:
            self.show_cursor = not self.show_cursor
            self.name_time = current_time

        # helper
        def key_pressed(k):
            return self._key_pressed(keyboard, k)

        # confirm / cancel
        if key_pressed('return') or getattr(keyboard, 'RETURN', False):
            name = self.name.strip()
            self.stop()
            return 'commit', name if name else None
        if key_pressed('escape') or getattr(keyboard, 'ESCAPE', False):
            self.stop()
            return 'cancel', None

        allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789 -_'

        mods = 0
        try:
            mods = pygame.key.get_mods()
        except Exception:
            mods = 0
        shift_on = bool(mods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT | pygame.KMOD_SHIFT))
        caps_on = bool(mods & pygame.KMOD_CAPS)

        pressed_chars = set(k for k in allowed_chars if key_pressed(k))
        backspace_now = key_pressed('backspace') or getattr(keyboard, 'BACKSPACE', False)

        # BACKSPACE handling
        if backspace_now:
            if 'BACKSPACE' not in self.prev_pressed_keys:
                if self.name:
                    self.name = self.name[:-1]
                self.key_last_time['BACKSPACE'] = current_time
                self.key_next_repeat['BACKSPACE'] = current_time + self.repeat_delay
            else:
                if current_time >= self.key_next_repeat.get('BACKSPACE', 0) and (
                    current_time - self.key_last_time.get('BACKSPACE', 0) >= self.repeat_interval):
                    if self.name:
                        self.name = self.name[:-1]
                    self.key_last_time['BACKSPACE'] = current_time
                    self.key_next_repeat['BACKSPACE'] = current_time + self.repeat_interval

        # Character handling
        new_presses = pressed_chars - self.prev_pressed_keys
        held = pressed_chars & self.prev_pressed_keys

        for ch in new_presses:
            if len(self.name) < self.max_length:
                actual = ch
                if ch.isalpha():
                    if shift_on ^ caps_on:
                        actual = ch.upper()
                elif ch == '-':
                    if shift_on:
                        actual = '_'
                self.name += actual
                self.key_last_time[ch] = current_time
                self.key_next_repeat[ch] = current_time + self.repeat_delay
                break

        if not new_presses:
            for ch in held:
                next_time = self.key_next_repeat.get(ch, 0)
                last_time = self.key_last_time.get(ch, 0)
                if current_time >= next_time and (current_time - last_time) >= self.repeat_interval:
                    if len(self.name) < self.max_length:
                        actual = ch
                        if ch.isalpha():
                            if shift_on ^ caps_on:
                                actual = ch.upper()
                        elif ch == '-':
                            if shift_on:
                                actual = '_'
                        self.name += actual
                        self.key_last_time[ch] = current_time
                        self.key_next_repeat[ch] = current_time + self.repeat_interval
                        break

        # update prev pressed
        self.prev_pressed_keys = set(pressed_chars)

        return 'idle', None
