"""Persistence helpers: settings, player name, and high score storage.

This module centralises reading/writing JSON files and exposes simple
functions that the game can call. It uses atomic writes to reduce risk of
corruption.
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict
from constants import DEFAULT_PLAYER_NAME, MAX_TOP_SCORES


def get_data_dir() -> str:
    try:
        if os.name == 'nt':
            appdata = os.getenv('APPDATA') or os.path.expanduser('~')
            path = os.path.join(appdata, 'LunarLander')
        elif sys.platform == 'darwin':
            path = os.path.expanduser('~/Library/Application Support/LunarLander')
        else:
            path = os.path.expanduser('~/.local/share/lander')
        os.makedirs(path, exist_ok=True)
        return path
    except Exception:
        return os.getcwd()


DATA_DIR = get_data_dir()
PLAYER_FILE = os.path.join(DATA_DIR, 'player.json')
SCORES_FILE = os.path.join(DATA_DIR, 'scores.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')


DEFAULT_SETTINGS = {'save_player': True, 'save_scores': True}


def atomic_write_json(path: str, data) -> None:
    try:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def load_settings() -> dict:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return DEFAULT_SETTINGS.copy()
                s = DEFAULT_SETTINGS.copy()
                s.update(data)
                return s
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        atomic_write_json(SETTINGS_FILE, settings)
    except Exception:
        pass


# Load runtime settings (simple module-level flags)
_runtime_settings = load_settings()
SAVE_PLAYER = bool(_runtime_settings.get('save_player', True))
SAVE_SCORES = bool(_runtime_settings.get('save_scores', True))


def load_player_name() -> str:
    try:
        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get('name', DEFAULT_PLAYER_NAME)
    except Exception:
        pass
    return DEFAULT_PLAYER_NAME


def save_player_name(name: str) -> None:
    if not SAVE_PLAYER:
        return
    try:
        atomic_write_json(PLAYER_FILE, {'name': name})
    except Exception:
        pass


def load_scores() -> List[Dict]:
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'high_score' in data:
                    return [{'score': data['high_score'], 'player': DEFAULT_PLAYER_NAME,
                             'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'stats': None}]
                if isinstance(data, list):
                    valid = [item for item in data if isinstance(item, dict) and 'score' in item and 'player' in item and 'date' in item]
                    return valid
    except Exception:
        pass
    return []


def save_new_score(score: int, stats: dict, player: str = DEFAULT_PLAYER_NAME) -> List[Dict]:
    try:
        scores = load_scores()
        new_score = {'score': score, 'player': player,
                     'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'stats': stats}
        scores.append(new_score)
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:MAX_TOP_SCORES]
        if SAVE_SCORES:
            atomic_write_json(SCORES_FILE, scores)
        return scores
    except Exception:
        return []
