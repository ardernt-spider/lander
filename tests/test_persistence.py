"""Test persistence module."""
import os
import json
import shutil
from datetime import datetime
import pytest
from persistence import (
    save_settings, load_settings,
    save_player_name, load_player_name,
    save_new_score, load_scores,
    DEFAULT_SETTINGS, DEFAULT_PLAYER_NAME, MAX_TOP_SCORES,
    DATA_DIR
)

@pytest.fixture(autouse=True)
def clean_data_dir(temp_data_dir):
    """Clean up data directory before each test."""
    # Always set default settings for testing
    save_settings(DEFAULT_SETTINGS)
    
    # Remove any existing data files
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            file_path = os.path.join(DATA_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def test_settings_save_load(temp_data_dir):
    """Test saving and loading settings."""
    custom_settings = {'save_player': False, 'save_scores': True}
    
    # Save settings
    save_settings(custom_settings)
    
    # Load settings
    loaded_settings = load_settings()
    assert loaded_settings == custom_settings

def test_settings_load_defaults(temp_data_dir):
    """Test loading default settings when no file exists."""
    settings = load_settings()
    assert settings == DEFAULT_SETTINGS

def test_player_name_save_load(temp_data_dir):
    """Test saving and loading player name."""
    test_name = "Test Player"
    
    # Save name
    save_player_name(test_name)
    
    # Load name
    loaded_name = load_player_name()
    assert loaded_name == test_name

def test_player_name_load_default(temp_data_dir):
    """Test loading default player name when no file exists."""
    name = load_player_name()
    assert name == DEFAULT_PLAYER_NAME

def test_scores_save_load(temp_data_dir):
    """Test saving and loading scores."""
    # Create test score and stats data
    score = 1000
    stats = {
        'total': score,  # Score should match
        'base': 1000,
        'speed': 200,
        'position': 300,
        'fuel': 400,
        'time': 100,
        'speed_value': 45.5,
        'distance': 10.0,
        'mission_time': 30000
    }
    player = "Test Player"
    
    # Save score
    top_scores = save_new_score(score, stats, player)
    assert len(top_scores) == 1
    assert top_scores[0]['score'] == score
    assert top_scores[0]['player'] == player
    assert isinstance(top_scores[0]['date'], str)
    
    # Load scores
    loaded_scores = load_scores()
    assert loaded_scores == top_scores

def test_scores_limit(temp_data_dir):
    """Test that scores list is limited to MAX_TOP_SCORES."""
    # Add more scores than the limit
    scores = []
    for i in range(MAX_TOP_SCORES + 5):
        score = (MAX_TOP_SCORES + 5 - i) * 100  # Higher scores first
        stats = {
            'total': score,
            'speed': 200,
            'position': 300,
            'fuel': 400,
            'time': 100,
            'speed_value': 45.5,
            'distance': 10.0,
            'mission_time': 30000
        }
        scores = save_new_score(score, stats, f"Player {i}")
    
    # Verify limit is enforced
    assert len(scores) == MAX_TOP_SCORES
    # Verify scores are sorted highest first
    for i in range(len(scores) - 1):
        assert scores[i]['score'] >= scores[i + 1]['score']

def test_scores_merge_sort(temp_data_dir):
    """Test that new scores are merged and sorted correctly."""
    # Add some initial scores
    # Create base stats that we'll modify for each score
    base_stats = {
        'base': 1000,
        'speed': 200,
        'position': 300,
        'fuel': 400,
        'time': 100,
        'speed_value': 45.5,
        'distance': 10.0,
        'mission_time': 30000
    }
    
    # Create stats for each score
    stats1 = {**base_stats, 'total': 1000}
    stats2 = {**base_stats, 'total': 500}
    
    save_new_score(1000, stats1, "Player 1")
    save_new_score(500, stats2, "Player 2")
    
    # Add a middle score
    stats3 = {**base_stats, 'total': 750}
    scores = save_new_score(750, stats3, "Player 3")
    
    # Verify order
    assert [s['score'] for s in scores] == [1000, 750, 500]
    assert [s['player'] for s in scores] == ["Player 1", "Player 3", "Player 2"]