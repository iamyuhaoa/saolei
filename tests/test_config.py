"""Tests for configuration module."""

import pytest
import numpy as np
from src.config import MinesweeperConfig, config


@pytest.mark.unit
def test_config_is_immutable():
    """Test that config is immutable (frozen dataclass)."""
    with pytest.raises(Exception):  # FrozenInstanceError or similar
        config.WINDOW_TITLE_PATTERN = "different"


@pytest.mark.unit
def test_config_has_required_constants():
    """Test that all required constants are defined."""
    assert hasattr(config, "WINDOW_CLASS_PRIORITY")
    assert hasattr(config, "STATE_COVERED")
    assert hasattr(config, "STATE_FLAGGED")
    assert hasattr(config, "STATE_MINE")


@pytest.mark.unit
def test_window_class_priority_is_tuple():
    """Test that WINDOW_CLASS_PRIORITY is immutable tuple."""
    assert isinstance(config.WINDOW_CLASS_PRIORITY, tuple)
    assert len(config.WINDOW_CLASS_PRIORITY) == 3


@pytest.mark.unit
def test_number_colors_complete():
    """Test that all numbers 1-8 have color definitions."""
    for i in range(1, 9):
        assert str(i) in config.NUMBER_COLORS
        color = config.NUMBER_COLORS[str(i)]
        assert isinstance(color, tuple)
        assert len(color) == 3
        # Verify BGR values are in valid range
        for value in color:
            assert 0 <= value <= 255


@pytest.mark.unit
def test_color_arrays_are_correct_shape():
    """Test that color threshold arrays are correctly shaped."""
    lower = config.COLOR_COVERED_LOWER
    upper = config.COLOR_COVERED_UPPER
    assert lower.shape == (3,)
    assert upper.shape == (3,)


@pytest.mark.unit
def test_difficulty_levels():
    """Test that all difficulty levels are defined."""
    assert "beginner" in config.DIFFICULTY_LEVELS
    assert "intermediate" in config.DIFFICULTY_LEVELS
    assert "expert" in config.DIFFICULTY_LEVELS

    # Verify format: (rows, cols, mines)
    for level, (rows, cols, mines) in config.DIFFICULTY_LEVELS.items():
        assert rows > 0
        assert cols > 0
        assert mines > 0
        assert mines < rows * cols  # Can't have more mines than cells


@pytest.mark.unit
def test_get_color_thresholds():
    """Test that get_color_thresholds returns correct structure."""
    thresholds = config.get_color_thresholds()
    assert "covered" in thresholds
    assert "flag" in thresholds
    assert "mine" in thresholds

    for state, thresh in thresholds.items():
        assert "lower" in thresh
        assert "upper" in thresh
        assert isinstance(thresh["lower"], np.ndarray)
        assert isinstance(thresh["upper"], np.ndarray)


@pytest.mark.unit
def test_config_values_are_positive():
    """Test that numeric config values are positive."""
    assert config.COLOR_TOLERANCE > 0
    assert config.TEMPLATE_MATCH_THRESHOLD > 0
    assert config.TEMPLATE_MATCH_THRESHOLD <= 1.0
    assert config.MIN_CELL_SIZE > 0
    assert config.MAX_CELL_SIZE > config.MIN_CELL_SIZE
    assert config.MAX_CONFIGURATIONS > 0
    assert config.ACTION_DELAY >= 0
