"""AI solver using constraint satisfaction and probability calculation."""

import logging
from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict
from itertools import combinations

import numpy as np

from src.config import config
from src.board_manager import get_neighbors

logger = logging.getLogger(__name__)


def is_numbered_cell(cell_state: str) -> bool:
    """Check if a cell contains a number."""
    return cell_state.isdigit() and cell_state != "0"


def get_cell_value(cell_state: str) -> int:
    """Extract numeric value from a numbered cell."""
    if is_numbered_cell(cell_state):
        return int(cell_state)
    return 0


def get_numbered_cells(board: np.ndarray) -> List[Tuple[int, int]]:
    """Get all cells that contain numbers."""
    numbered = []
    for row in range(board.shape[0]):
        for col in range(board.shape[1]):
            if is_numbered_cell(board[row, col]):
                numbered.append((row, col))
    return numbered


def get_unrevealed_neighbors(
    board: np.ndarray, row: int, col: int
) -> Set[Tuple[int, int]]:
    """Get all unrevealed neighbors of a cell."""
    neighbors = get_neighbors(board.shape[0], board.shape[1], row, col)
    return {n for n in neighbors if board[n] == config.STATE_COVERED}


def get_flagged_neighbors(
    board: np.ndarray, row: int, col: int
) -> Set[Tuple[int, int]]:
    """Get all flagged neighbors of a cell."""
    neighbors = get_neighbors(board.shape[0], board.shape[1], row, col)
    return {n for n in neighbors if board[n] == config.STATE_FLAGGED}


def apply_logic_rules(board: np.ndarray) -> List[Tuple[Tuple[int, int], str]]:
    """
    Apply deterministic logic rules to find certain moves.

    Args:
        board: Current board state

    Returns:
        List of ((row, col), action) where action is 'reveal' or 'flag'
    """
    moves = []
    rows, cols = board.shape

    for r, c in get_numbered_cells(board):
        number = get_cell_value(board[r, c])
        neighbors = get_neighbors(rows, cols, r, c)
        unrevealed = get_unrevealed_neighbors(board, r, c)
        flagged = get_flagged_neighbors(board, r, c)

        # Rule 1: If unrevealed + flagged == number, all unrevealed are mines
        if len(unrevealed) + len(flagged) == number:
            for nr, nc in unrevealed:
                moves.append(((nr, nc), "flag"))

        # Rule 2: If flagged == number, all unrevealed are safe
        if len(flagged) == number:
            for nr, nc in unrevealed:
                moves.append(((nr, nc), "reveal"))

    return moves


def build_constraint_set(board: np.ndarray) -> List[Tuple[Set[Tuple[int, int]], int]]:
    """
    Build a set of constraints from the board state.

    Each constraint: (set_of_cells, required_mine_count)

    Args:
        board: Current board state

    Returns:
        List of constraints
    """
    constraints = []
    rows, cols = board.shape

    for r, c in get_numbered_cells(board):
        number = get_cell_value(board[r, c])
        unrevealed = get_unrevealed_neighbors(board, r, c)

        if unrevealed:
            constraints.append((unrevealed, number))

    return constraints


def enumerate_valid_configurations(
    constraints: List[Tuple[Set[Tuple[int, int]], int]], max_iterations: int = 10000
) -> List[Set[Tuple[int, int]]]:
    """
    Enumerate valid mine configurations that satisfy all constraints.

    Args:
        constraints: List of (cell_set, required_mines) constraints
        max_iterations: Maximum number of configurations to enumerate

    Returns:
        List of sets containing mine positions for each valid configuration
    """
    valid_configs = []

    # Group cells that appear in constraints
    all_cells = set()
    for cells, _ in constraints:
        all_cells.update(cells)

    if not all_cells:
        return valid_configs

    # Try each possible number of mines
    for num_mines in range(len(all_cells) + 1):
        for mine_combination in combinations(all_cells, num_mines):
            mine_set = set(mine_combination)

            # Check if this configuration satisfies all constraints
            satisfies_all = True
            for cells, required_count in constraints:
                actual_count = len(mine_set & cells)
                if actual_count != required_count:
                    satisfies_all = False
                    break

            if satisfies_all:
                valid_configs.append(mine_set)

            if len(valid_configs) >= max_iterations:
                return valid_configs

    return valid_configs


def calculate_probabilities(board: np.ndarray) -> Dict[Tuple[int, int], float]:
    """
    Calculate mine probabilities for all covered cells.

    Args:
        board: Current board state

    Returns:
        Dictionary mapping (row, col) -> probability (0.0 to 1.0)
    """
    constraints = build_constraint_set(board)

    if not constraints:
        # No constraints, use simple probability
        return calculate_simple_probability(board)

    valid_configs = enumerate_valid_configurations(
        constraints, config.MAX_CONFIGURATIONS
    )

    if not valid_configs:
        return calculate_simple_probability(board)

    # Count how many times each cell is a mine
    mine_counts = defaultdict(int)
    for config_mines in valid_configs:
        for cell in config_mines:
            mine_counts[cell] += 1

    # Calculate probabilities
    probabilities = {}
    total_configs = len(valid_configs)

    for cell in mine_counts:
        probabilities[cell] = mine_counts[cell] / total_configs

    return probabilities


def calculate_simple_probability(
    board: np.ndarray, total_mines: Optional[int] = None
) -> Dict[Tuple[int, int], float]:
    """
    Calculate simple probability based on total mines and covered cells.

    Args:
        board: Current board state
        total_mines: Total number of mines (optional, estimates if None)

    Returns:
        Dictionary mapping (row, col) -> probability
    """
    covered_cells = []
    flagged_count = 0

    for row in range(board.shape[0]):
        for col in range(board.shape[1]):
            if board[row, col] == config.STATE_COVERED:
                covered_cells.append((row, col))
            elif board[row, col] == config.STATE_FLAGGED:
                flagged_count += 1

    if not covered_cells:
        return {}

    # Estimate total mines based on difficulty if not provided
    if total_mines is None:
        rows, cols = board.shape
        # Guess difficulty based on board size
        if (rows, cols) == (9, 9):
            total_mines = 10  # Beginner
        elif (rows, cols) == (16, 16):
            total_mines = 40  # Intermediate
        elif (rows, cols) == (16, 30):
            total_mines = 99  # Expert
        else:
            # Conservative estimate: 15%
            total_mines = int((rows * cols) * 0.15)

    # Calculate probability: remaining mines / covered cells
    remaining_mines = max(0, total_mines - flagged_count)
    probability = remaining_mines / len(covered_cells) if covered_cells else 0

    return {cell: probability for cell in covered_cells}


def get_safest_cell(
    probabilities: Dict[Tuple[int, int], float],
) -> Optional[Tuple[int, int]]:
    """
    Find the cell with the lowest mine probability.

    Args:
        probabilities: Dictionary of cell probabilities

    Returns:
        (row, col) of safest cell or None if no probabilities
    """
    if not probabilities:
        return None

    return min(probabilities.items(), key=lambda x: x[1])[0]


class MinesweeperSolver:
    """AI solver for Minesweeper using logic and probability."""

    def __init__(self) -> None:
        """Initialize the solver."""
        self.board: Optional[np.ndarray] = None

    def solve(self, board: np.ndarray) -> List[Tuple[Tuple[int, int], str]]:
        """
        Determine the next move(s).

        Args:
            board: Current board state

        Returns:
            List of ((row, col), action) where action is 'reveal' or 'flag'
        """
        self.board = board

        # Phase 1: Try logic-based deterministic solution
        if config.ENABLE_LOGIC_RULES:
            moves = apply_logic_rules(board)
            if moves:
                logger.info(f"Found {len(moves)} deterministic moves")
                return moves

        # Phase 2: Probability-based solution
        if config.ENABLE_PROBABILITY_CALCULATION:
            probabilities = calculate_probabilities(board)

            if probabilities:
                safest_cell = get_safest_cell(probabilities)
                if safest_cell:
                    prob = probabilities[safest_cell]
                    logger.info(
                        f"Choosing safest cell {safest_cell} with probability {prob:.2f}"
                    )
                    return [(safest_cell, "reveal")]

        # No good options - make a guess
        logger.warning("No clear moves found, guessing")
        return self._make_guess(board)

    def _make_guess(self, board: np.ndarray) -> List[Tuple[Tuple[int, int], str]]:
        """
        Make a guess when no logical moves are available.

        Args:
            board: Current board state

        Returns:
            List with a single guess move
        """
        # Prefer corners and edges (statistically safer)
        rows, cols = board.shape

        # Try corners first
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        for r, c in corners:
            if board[r, c] == config.STATE_COVERED:
                return [((r, c), "reveal")]

        # Try edges
        for c in range(cols):
            if board[0, c] == config.STATE_COVERED:
                return [((0, c), "reveal")]
            if board[rows - 1, c] == config.STATE_COVERED:
                return [((rows - 1, c), "reveal")]

        # Pick first covered cell
        for r in range(rows):
            for c in range(cols):
                if board[r, c] == config.STATE_COVERED:
                    return [((r, c), "reveal")]

        return []

    def update_board(self, row: int, col: int, new_state: str) -> None:
        """
        Update board state after a move.

        Args:
            row: Cell row
            col: Cell column
            new_state: New state of the cell
        """
        if self.board is not None:
            self.board[row, col] = new_state
