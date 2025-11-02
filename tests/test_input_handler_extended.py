import types
import pytest
import pygame

from input_handler import TextInputHandler


class FakeKeyboard:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cursor_blink_behavior(monkeypatch):
    handler = TextInputHandler()
    t = {'now': 0}

    def fake_ticks():
        return t['now']
    
    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)
    
    # Initial state should always show cursor
    handler.start('test')
    handler.show_cursor = True
    assert handler.get_display_text() == 'test_'
    
    # Test basic cursor toggle states
    handler.show_cursor = False
    assert handler.get_display_text() == 'test '
    handler.show_cursor = True
    assert handler.get_display_text() == 'test_'
    
    # Test time-based updates at 500ms intervals
    t['now'] = 0
    handler.name_time = 0
    initial_state = handler.show_cursor
    
    # No change before 500ms
    t['now'] = 400
    handler.update(FakeKeyboard())
    assert handler.show_cursor == initial_state
    
    # State updates happen on 500ms boundaries
    displays = set()
    for time in range(0, 2000, 500):
        t['now'] = time
        handler.update(FakeKeyboard())
        displays.add(handler.get_display_text())
    
    # Should see both cursor states over time
    assert len(displays) == 2
    assert 'test_' in displays
    assert 'test ' in displays


def test_enter_and_cancel(monkeypatch):
    handler = TextInputHandler()
    
    pressed = set()
    def _key_pressed(self, keyboard, k):
        return k in pressed
    handler._key_pressed = types.MethodType(_key_pressed, handler)
    
    handler.start('test')
    
    # Test enter with non-empty name
    pressed.add('return')
    status, name = handler.update(FakeKeyboard())
    assert status == 'commit'
    assert name == 'test'
    assert not handler.entering
    
    # Test enter with empty/whitespace name
    handler.start('  ')
    pressed = {'return'}
    status, name = handler.update(FakeKeyboard())
    assert status == 'commit'
    assert name is None  # empty name returns None
    
    # Test escape
    handler.start('test')
    pressed = {'escape'}
    status, name = handler.update(FakeKeyboard())
    assert status == 'cancel'
    assert name is None
    assert not handler.entering


def test_shift_and_caps_handling(monkeypatch):
    handler = TextInputHandler()
    t = {'now': 0}
    
    def fake_ticks():
        return t['now']
    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)
    
    pressed = set()
    mods = 0
    
    def _key_pressed(self, keyboard, k):
        return k in pressed
    
    def fake_get_mods():
        return mods
    
    handler._key_pressed = types.MethodType(_key_pressed, handler)
    monkeypatch.setattr(pygame.key, 'get_mods', fake_get_mods)
    
    handler.start()
    
    # Test shift for uppercase
    pressed.add('a')
    mods = pygame.KMOD_LSHIFT
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'A'
    
    # Test caps lock
    pressed = {'b'}
    mods = pygame.KMOD_CAPS
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'AB'
    
    # Test shift with caps (should cancel out)
    pressed = {'c'}
    mods = pygame.KMOD_CAPS | pygame.KMOD_LSHIFT
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'ABc'
    
    # Test hyphen/underscore
    pressed = {'-'}
    mods = 0
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'ABc-'
    
    # Test underscore (press - with shift)
    pressed = {'-'}
    mods = pygame.KMOD_LSHIFT
    handler.prev_pressed_keys.clear()  # Release previous key to trigger new press
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'ABc-_'


def test_max_length_limit(monkeypatch):
    handler = TextInputHandler(max_length=5)
    t = {'now': 0}
    
    def fake_ticks():
        return t['now']
    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)
    
    pressed = set()
    def _key_pressed(self, keyboard, k):
        return k in pressed
    handler._key_pressed = types.MethodType(_key_pressed, handler)
    
    handler.start()
    
    # Fill to max length
    for ch in 'abcde':
        pressed = {ch}
        status, _ = handler.update(FakeKeyboard())
        
    # Try to add more characters
    pressed = {'f'}
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'abcde'  # should not change
    
    # Ensure backspace still works at max length
    pressed = {'backspace'}
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'abcd'
    
    # Can add another character after backspace
    pressed = {'f'}
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'abcdf'


def test_pgzero_keyboard_compatibility(monkeypatch):
    handler = TextInputHandler()
    t = {'now': 0}
    
    def fake_ticks():
        return t['now']
    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)
    
    pressed = set()
    def _key_pressed(self, keyboard, k):
        if hasattr(keyboard, k):
            return True
        if k.lower() == 'a' and k in pressed:
            return True
        return False
    handler._key_pressed = types.MethodType(_key_pressed, handler)
    
    handler.start()
    
    # Test pgzero-style keyboard attributes
    pressed.add('a')  # Simulate pygame key press
    keyboard = FakeKeyboard(a=True)  # Simulate pgzero attribute
    status, _ = handler.update(keyboard)
    assert handler.name == 'a'
    
    # Test return key
    pressed.add('return')
    keyboard = FakeKeyboard(RETURN=True)
    status, name = handler.update(keyboard)
    assert status == 'commit'
    
    # Test mixed pygame/pgzero input
    handler.start()
    keyboard = FakeKeyboard(ESCAPE=True)
    status, name = handler.update(keyboard)
    assert status == 'cancel'


def test_error_handling(monkeypatch):
    handler = TextInputHandler()
    
    def fake_ticks():
        return 0
    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)
    
    # Test graceful handling of keyboard attribute errors
    status, name = handler.update(None)
    assert status == 'idle'  # should not crash
    
    # Test handling of pygame.key errors
    def raise_error(*args):
        raise Exception("Pygame error")
    
    monkeypatch.setattr(pygame.key, 'get_pressed', raise_error)
    monkeypatch.setattr(pygame.key, 'get_mods', raise_error)
    
    handler.start('test')
    status, name = handler.update(FakeKeyboard())
    assert status == 'idle'  # should not crash
    assert handler.name == 'test'  # should preserve existing name