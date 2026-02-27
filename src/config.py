"""Configuration constants for Minesweeper AI solver."""

import logging
from typing import Final, Mapping, Tuple
from dataclasses import dataclass, field
import numpy as np


# Define constants at module level for immutability
_WINDOW_CLASS_PRIORITY: Final = (
    "Minesweeper",  # Windows 7 classic
    "Windows.UI.Core.CoreWindow",  # Windows 10/11 modern
    "UnityWndClass",  # Some remakes
)

_NUMBER_COLORS: Mapping[str, Tuple[int, int, int]] = {
    "1": (0, 0, 255),      # Blue
    "2": (0, 128, 0),      # Green
    "3": (0, 0, 128),      # Red
    "4": (128, 0, 0),      # Dark blue
    "5": (128, 0, 128),    # Dark red/maroon
    "6": (0, 128, 128),    # Cyan
    "7": (0, 0, 0),        # Black
    "8": (128, 128, 128),  # Gray
}

_DIFFICULTY_LEVELS: Mapping[str, Tuple[int, int, int]] = {
    "beginner": (9, 9, 10),
    "intermediate": (16, 16, 40),
    "expert": (16, 30, 99),
}


@dataclass(frozen=True)
class MinesweeperConfig:
    """Immutable configuration for Minesweeper AI solver."""

    # Window detection configuration
    WINDOW_CLASS_PRIORITY: Tuple[str, ...] = field(default_factory=lambda: _WINDOW_CLASS_PRIORITY)
    WINDOW_TITLE_PATTERN: str = ".*[Mm]inesweeper.*"

    # Cell state constants
    STATE_COVERED: str = "covered"
    STATE_UNCOVERED: str = "uncovered"
    STATE_FLAGGED: str = "flagged"
    STATE_MINE: str = "mine"
    STATE_UNKNOWN: str = "unknown"

    # Color thresholds for cell detection (BGR format)
    # Gray range for covered cells
    COLOR_COVERED_LOWER: np.ndarray = field(default_factory=lambda: np.array([180, 180, 180]))
    COLOR_COVERED_UPPER: np.ndarray = field(default_factory=lambda: np.array([200, 200, 200]))

    # Red range for flagged cells
    COLOR_FLAG_LOWER: np.ndarray = field(default_factory=lambda: np.array([0, 0, 200]))
    COLOR_FLAG_UPPER: np.ndarray = field(default_factory=lambda: np.array([50, 50, 255]))

    # Black range for mines
    COLOR_MINE_LOWER: np.ndarray = field(default_factory=lambda: np.array([0, 0, 0]))
    COLOR_MINE_UPPER: np.ndarray = field(default_factory=lambda: np.array([30, 30, 30]))

    # Number colors (BGR format) for Minesweeper digits
    NUMBER_COLORS: Mapping[str, Tuple[int, int, int]] = field(default_factory=lambda: _NUMBER_COLORS)

    # Image processing parameters
    COLOR_TOLERANCE: int = 30
    TEMPLATE_MATCH_THRESHOLD: float = 0.7
    MIN_CELL_SIZE: int = 10
    MAX_CELL_SIZE: int = 100

    # Solver configuration
    MAX_CONFIGURATIONS: int = 10000
    ENABLE_LOGIC_RULES: bool = True
    ENABLE_PROBABILITY_CALCULATION: bool = True

    # Mouse control parameters
    ACTION_DELAY: float = 0.1  # Seconds between actions
    ENABLE_SAFETY: bool = True

    # Logging configuration
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Difficulty levels: (rows, cols, mines)
    DIFFICULTY_LEVELS: Mapping[str, Tuple[int, int, int]] = field(default_factory=lambda: _DIFFICULTY_LEVELS)

    def get_color_thresholds(self) -> dict:
        """Get color thresholds as a dictionary."""
        return {
            "covered": {
                "lower": self.COLOR_COVERED_LOWER,
                "upper": self.COLOR_COVERED_UPPER
            },
            "flag": {
                "lower": self.COLOR_FLAG_LOWER,
                "upper": self.COLOR_FLAG_UPPER
            },
            "mine": {
                "lower": self.COLOR_MINE_LOWER,
                "upper": self.COLOR_MINE_UPPER
            },
        }


# Global configuration instance
config: MinesweeperConfig = MinesweeperConfig()
