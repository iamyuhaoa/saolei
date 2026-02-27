"""Mouse control for interacting with Minesweeper window."""

import logging
import sys
import time
from typing import Tuple

from src.config import config

logger = logging.getLogger(__name__)

# Check if running on Windows
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    from pywinauto import mouse
else:
    # Mock for non-Windows platforms
    mouse = None


class MouseController:
    """Controls mouse interaction with the Minesweeper window."""

    def __init__(
        self,
        window_hwnd: int,
        window_rect: Tuple[int, int, int, int],
        enable_safety: bool = True,
        min_action_delay: float = 0.1
    ) -> None:
        """
        Initialize MouseController.

        Args:
            window_hwnd: Window handle
            window_rect: Window rectangle (left, top, right, bottom)
            enable_safety: Whether to enable rate limiting
            min_action_delay: Minimum delay between actions in seconds
        """
        self.window_hwnd = window_hwnd
        self.window_rect = window_rect
        self.enable_safety = enable_safety
        self.min_action_delay = min_action_delay
        self.last_action_time = 0.0

    def _cell_to_screen_coords(
        self,
        row: int,
        col: int,
        grid_origin: Tuple[int, int],
        cell_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Convert board cell coordinates to screen coordinates.

        Args:
            row: Cell row index
            col: Cell column index
            grid_origin: Grid origin (x, y) within window
            cell_size: Cell size (width, height)

        Returns:
            Tuple of (screen_x, screen_y) representing center of cell
        """
        origin_x, origin_y = grid_origin
        cell_width, cell_height = cell_size
        window_left, window_top, _, _ = self.window_rect

        # Calculate screen position
        screen_x = window_left + origin_x + col * cell_width + cell_width // 2
        screen_y = window_top + origin_y + row * cell_height + cell_height // 2

        return screen_x, screen_y

    def click_cell(
        self,
        row: int,
        col: int,
        grid_origin: Tuple[int, int],
        cell_size: Tuple[int, int],
        button: str = "left"
    ) -> None:
        """
        Click on a specific cell.

        Args:
            row: Cell row index
            col: Cell column index
            grid_origin: Grid origin (x, y) within window
            cell_size: Cell size (width, height)
            button: 'left' for reveal, 'right' for flag

        Raises:
            NotImplementedError: If not running on Windows
        """
        if not IS_WINDOWS:
            raise NotImplementedError("Mouse control is only supported on Windows")

        # Rate limiting
        if self.enable_safety:
            current_time = time.time()
            elapsed = current_time - self.last_action_time
            if elapsed < self.min_action_delay:
                time.sleep(self.min_action_delay - elapsed)
            self.last_action_time = time.time()

        # Get screen coordinates
        x, y = self._cell_to_screen_coords(row, col, grid_origin, cell_size)

        # Perform click
        try:
            mouse.move(coords=(x, y))
            if button == "left":
                mouse.click(button="left", coords=(x, y))
            elif button == "right":
                mouse.click(button="right", coords=(x, y))
            else:
                raise ValueError(f"Invalid button: {button}")

            logger.debug(f"Clicked {button} at ({row}, {col}) -> screen ({x}, {y})")

        except Exception as e:
            logger.error(f"Failed to click cell ({row}, {col}): {e}")
            raise

    def reveal_cell(
        self,
        row: int,
        col: int,
        grid_origin: Tuple[int, int],
        cell_size: Tuple[int, int]
    ) -> None:
        """
        Reveal a cell (left click).

        Args:
            row: Cell row index
            col: Cell column index
            grid_origin: Grid origin (x, y) within window
            cell_size: Cell size (width, height)
        """
        self.click_cell(row, col, grid_origin, cell_size, button="left")

    def flag_cell(
        self,
        row: int,
        col: int,
        grid_origin: Tuple[int, int],
        cell_size: Tuple[int, int]
    ) -> None:
        """
        Flag a cell (right click).

        Args:
            row: Cell row index
            col: Cell column index
            grid_origin: Grid origin (x, y) within window
            cell_size: Cell size (width, height)
        """
        self.click_cell(row, col, grid_origin, cell_size, button="right")
