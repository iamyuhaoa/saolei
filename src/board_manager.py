"""Board state recognition using computer vision."""

import logging
from typing import Optional, Tuple, List, Set, Dict

import cv2
import numpy as np

from src.config import config

logger = logging.getLogger(__name__)


def detect_grid_structure(
    image: np.ndarray,
) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Detect the Minesweeper grid structure in an image.

    Args:
        image: BGR image of the Minesweeper window

    Returns:
        Tuple of (cell_size, grid_origin) or None if detection fails
        - cell_size: (width, height) of a single cell
        - grid_origin: (x, y) coordinates of top-left grid corner
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection to find grid lines
        edges = cv2.Canny(gray, 50, 150)

        # Find contours to detect cell boundaries
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Analyze contours to find uniform grid pattern
        cell_sizes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if (
                config.MIN_CELL_SIZE < w < config.MAX_CELL_SIZE
                and config.MIN_CELL_SIZE < h < config.MAX_CELL_SIZE
            ):
                cell_sizes.append((w, h))

        if not cell_sizes:
            logger.warning("No cells detected in image")
            return None

        # Find most common cell size using clustering
        cell_sizes = np.array(cell_sizes)

        # Simple clustering: find median size
        median_width = int(np.median(cell_sizes[:, 0]))
        median_height = int(np.median(cell_sizes[:, 1]))

        # Estimate grid origin from contour positions
        min_x = int(np.min([cv2.boundingRect(cnt)[0] for cnt in contours]))
        min_y = int(np.min([cv2.boundingRect(cnt)[1] for cnt in contours]))

        cell_size = (median_width, median_height)
        grid_origin = (min_x, min_y)

        logger.info(f"Detected grid: cell_size={cell_size}, origin={grid_origin}")
        return cell_size, grid_origin

    except Exception as e:
        logger.error(f"Failed to detect grid structure: {e}")
        return None


def classify_cell(
    cell_image: np.ndarray, color_thresholds: Dict[str, Dict[str, np.ndarray]]
) -> str:
    """
    Classify a single cell's state based on color.

    Args:
        cell_image: Image of a single cell (BGR)
        color_thresholds: Dictionary of color thresholds with 'lower' and 'upper' keys

    Returns:
        Cell state: 'covered', 'flagged', 'mine', 'uncovered', or 'unknown'
    """
    if cell_image.size == 0:
        return config.STATE_UNKNOWN

    # Get average color of the cell (more robust than single pixel)
    avg_color = np.mean(cell_image, axis=(0, 1))

    # Check mine first (very dark, almost black)
    mine_upper = color_thresholds["mine"]["upper"]
    if np.all(avg_color <= mine_upper):
        return config.STATE_MINE

    # Check flag (high red channel in BGR)
    flag_lower = color_thresholds["flag"]["lower"]
    flag_upper = color_thresholds["flag"]["upper"]
    if avg_color[2] >= flag_lower[2] and avg_color[2] <= flag_upper[2]:
        return config.STATE_FLAGGED

    # Check covered (gray range)
    covered_lower = color_thresholds["covered"]["lower"]
    covered_upper = color_thresholds["covered"]["upper"]
    if np.all(avg_color >= covered_lower) and np.all(avg_color <= covered_upper):
        return config.STATE_COVERED

    # Check if it's an uncovered cell (lighter background)
    # Uncovered cells typically have higher values
    if np.mean(avg_color) > 180:
        return config.STATE_UNCOVERED

    return config.STATE_UNKNOWN


def detect_board_size(
    image: np.ndarray, cell_size: Tuple[int, int], grid_origin: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Detect the number of rows and columns in the board.

    Args:
        image: Full window image
        cell_size: Size of each cell (width, height)
        grid_origin: Grid origin (x, y)

    Returns:
        Tuple of (rows, cols)
    """
    img_height, img_width = image.shape[:2]
    cell_width, cell_height = cell_size
    origin_x, origin_y = grid_origin

    # Calculate usable area
    usable_width = img_width - origin_x
    usable_height = img_height - origin_y

    # Calculate number of cells
    cols = usable_width // cell_width
    rows = usable_height // cell_height

    logger.info(f"Detected board size: {rows}x{cols}")
    return rows, cols


def get_neighbors(rows: int, cols: int, row: int, col: int) -> Set[Tuple[int, int]]:
    """
    Get all valid neighbor coordinates for a cell.

    Args:
        rows: Total number of rows in the board
        cols: Total number of columns in the board
        row: Cell's row index
        col: Cell's column index

    Returns:
        Set of (row, col) tuples representing neighbor coordinates

    Raises:
        ValueError: If row or col are out of bounds
    """
    if not (0 <= row < rows and 0 <= col < cols):
        raise ValueError(
            f"Cell coordinates ({row}, {col}) out of bounds for {rows}x{cols} board"
        )

    neighbors = set()

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue

            nr, nc = row + dr, col + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.add((nr, nc))

    return neighbors


def cell_coordinates_to_screen(
    row: int, col: int, grid_origin: Tuple[int, int], cell_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Convert board cell coordinates to screen coordinates.

    Args:
        row: Cell row index
        col: Cell column index
        grid_origin: Grid origin (x, y)
        cell_size: Cell size (width, height)

    Returns:
        Tuple of (screen_x, screen_y) representing center of cell
    """
    origin_x, origin_y = grid_origin
    cell_width, cell_height = cell_size

    screen_x = origin_x + col * cell_width + cell_width // 2
    screen_y = origin_y + row * cell_height + cell_height // 2

    return screen_x, screen_y


def screen_coordinates_to_cell(
    screen_x: int,
    screen_y: int,
    grid_origin: Tuple[int, int],
    cell_size: Tuple[int, int],
) -> Tuple[int, int]:
    """
    Convert screen coordinates to board cell coordinates.

    Args:
        screen_x: Screen x coordinate
        screen_y: Screen y coordinate
        grid_origin: Grid origin (x, y)
        cell_size: Cell size (width, height)

    Returns:
        Tuple of (row, col)
    """
    origin_x, origin_y = grid_origin
    cell_width, cell_height = cell_size

    col = (screen_x - origin_x) // cell_width
    row = (screen_y - origin_y) // cell_height

    return row, col


class BoardReader:
    """Reads and recognizes the Minesweeper board state."""

    def __init__(self) -> None:
        """Initialize BoardReader."""
        self.cell_size: Optional[Tuple[int, int]] = None
        self.grid_origin: Optional[Tuple[int, int]] = None
        self.rows: Optional[int] = None
        self.cols: Optional[int] = None
        self.color_thresholds = config.get_color_thresholds()

    def initialize(self, window_image: np.ndarray) -> bool:
        """
        Initialize grid detection on first run.

        Args:
            window_image: Image of the Minesweeper window

        Returns:
            True if initialization successful, False otherwise
        """
        result = detect_grid_structure(window_image)

        if result is None:
            return False

        self.cell_size, self.grid_origin = result
        self.rows, self.cols = detect_board_size(
            window_image, self.cell_size, self.grid_origin
        )

        return True

    def read_board(self, window_image: np.ndarray) -> np.ndarray:
        """
        Read the complete board state from window image.

        Args:
            window_image: Image of the Minesweeper window

        Returns:
            2D numpy array of cell states
        """
        if self.cell_size is None or self.grid_origin is None:
            raise RuntimeError("BoardReader not initialized. Call initialize() first.")

        board = np.empty((self.rows, self.cols), dtype=object)

        for row in range(self.rows):
            for col in range(self.cols):
                # Extract cell image
                x = self.grid_origin[0] + col * self.cell_size[0]
                y = self.grid_origin[1] + row * self.cell_size[1]
                cell_img = window_image[
                    y : y + self.cell_size[1], x : x + self.cell_size[0]
                ]

                # Classify cell
                board[row, col] = classify_cell(cell_img, self.color_thresholds)

        return board

    def update_board(
        self, window_image: np.ndarray, current_board: np.ndarray
    ) -> np.ndarray:
        """
        Read the current board state.

        Note: This currently re-reads the entire board. The current_board
        parameter is accepted for API compatibility but not used for
        delta detection (future optimization).

        Args:
            window_image: Current window image
            current_board: Current board state (unused, for future optimization)

        Returns:
            Current board state
        """
        return self.read_board(window_image)
