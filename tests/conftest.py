"""Test fixtures shared across test modules."""
import os
import sys
import tempfile
import pytest


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    old_env = {}
    if os.name == 'nt':
        old_env['APPDATA'] = os.environ.get('APPDATA')
    elif sys.platform == 'darwin':
        old_env['HOME'] = os.environ.get('HOME')
    else:
        old_env['XDG_DATA_HOME'] = os.environ.get('XDG_DATA_HOME')
        if not old_env['XDG_DATA_HOME']:
            old_env['HOME'] = os.environ.get('HOME')

    with tempfile.TemporaryDirectory() as tmp_dir:
        if os.name == 'nt':
            os.environ['APPDATA'] = tmp_dir
        elif sys.platform == 'darwin':
            os.environ['HOME'] = tmp_dir
        else:
            os.environ['XDG_DATA_HOME'] = tmp_dir

        yield tmp_dir

        # Restore original environment
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value