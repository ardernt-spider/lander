import sys
import traceback
import os

# Ensure repo root is on sys.path so tests can import modules from project
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def run():
    failures = 0
    try:
        from test_input_handler import (
            test_consume_initial_n,
            test_character_entry_and_repeat,
            test_backspace_and_repeat,
        )
    except Exception as e:
        print('Failed to import tests:', e)
        traceback.print_exc()
        return 2

    tests = [
        test_consume_initial_n,
        test_character_entry_and_repeat,
        test_backspace_and_repeat,
    ]

    class SimpleMonkeyPatch:
        def setattr(self, target, name, value):
            setattr(target, name, value)

    monkey = SimpleMonkeyPatch()

    for t in tests:
        try:
            # Our tests expect a monkeypatch argument
            t(monkey)
            print(f'PASS: {t.__name__}')
        except AssertionError as e:
            failures += 1
            print(f'FAIL: {t.__name__} - {e}')
            traceback.print_exc()
        except Exception as e:
            failures += 1
            print(f'ERROR: {t.__name__} - {e}')
            traceback.print_exc()

    if failures:
        print(f"{failures} test(s) failed")
        return 1
    print("All tests passed")
    return 0


if __name__ == '__main__':
    sys.exit(run())
