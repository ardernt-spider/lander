import types
import pygame
# pytest is optional; tests will run without it via tests/run_tests.py

from input_handler import TextInputHandler


class FakeKeyboard:
    # Minimal placeholder to satisfy TextInputHandler.update signature
    pass


def test_consume_initial_n(monkeypatch):
    handler = TextInputHandler(repeat_delay=200, repeat_interval=50)

    # Control time
    t = {'now': 0}

    def fake_ticks():
        return t['now']

    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)

    # Override low-level _key_pressed to consult our pressed set
    pressed = set()

    def _key_pressed(self, keyboard, k):
        return k in pressed

    handler._key_pressed = types.MethodType(_key_pressed, handler)

    # Start editing with consuming 'n'
    handler.start('Pilot', consume_keys={'n'})

    # Immediately after start, no extra 'n' should be appended
    status, name = handler.update(FakeKeyboard())
    assert status == 'idle'
    assert handler.name == 'Pilot'


def test_character_entry_and_repeat(monkeypatch):
    handler = TextInputHandler(repeat_delay=200, repeat_interval=50)
    t = {'now': 0}

    def fake_ticks():
        return t['now']

    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)

    pressed = set()

    def _key_pressed(self, keyboard, k):
        return k in pressed

    handler._key_pressed = types.MethodType(_key_pressed, handler)

    handler.start('', consume_keys=None)

    # Press 'a' (new press)
    pressed.add('a')
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'a'

    # Advance time less than repeat_delay: no extra char
    t['now'] = 100
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'a'

    # Advance time to trigger repeat
    t['now'] = 250
    status, _ = handler.update(FakeKeyboard())
    # second character should be appended due to repeat
    assert handler.name == 'aa'


def test_backspace_and_repeat(monkeypatch):
    handler = TextInputHandler(repeat_delay=200, repeat_interval=50)
    t = {'now': 0}

    def fake_ticks():
        return t['now']

    monkeypatch.setattr(pygame.time, 'get_ticks', fake_ticks)

    pressed = set()

    def _key_pressed(self, keyboard, k):
        # Accept both 'backspace' string used by handler
        return k in pressed

    handler._key_pressed = types.MethodType(_key_pressed, handler)

    handler.start('ab', consume_keys=None)

    # Press backspace once
    pressed.add('backspace')
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == 'a'

    # Hold backspace until repeat triggers
    t['now'] = 250
    status, _ = handler.update(FakeKeyboard())
    assert handler.name == ''
