"""Tests for solver module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch


@pytest.fixture
def sample_board():
    """Create a sample board for testing."""
    # 5x5 board with a simple configuration
    board = np.array([
        ['uncovered', 'uncovered', 'uncovered', 'covered', 'covered'],
        ['uncovered', '1', '1', 'covered', 'covered'],
        ['uncovered', 'covered', 'covered', 'covered', 'covered'],
        ['covered', 'covered', 'covered', 'covered', 'covered'],
        ['covered', 'covered', 'covered', 'covered', 'covered'],
    ], dtype=object)
    return board


@pytest.mark.unit
def test_apply_basic_logic_rule_all_mines(sample_board):
    """Test basic rule: all unrevealed neighbors are mines."""
    from src.solver import apply_logic_rules

    # Create board where a '1' has only 1 unrevealed neighbor
    board = np.array([
        ['covered', 'covered', 'covered'],
        ['covered', '1', 'covered'],
        ['covered', 'covered', 'covered'],
    ], dtype=object)

    # This should find some moves
    moves = apply_logic_rules(board)
    assert isinstance(moves, list)


@pytest.mark.unit
def test_apply_basic_logic_rule_all_safe(sample_board):
    """Test basic rule: all unrevealed neighbors are safe."""
    from src.solver import apply_logic_rules

    # Create board where a '1' has 1 flag and 1 uncovered neighbor
    board = np.array([
        ['covered', 'flagged', 'covered'],
        ['flagged', '1', 'covered'],
        ['covered', 'covered', 'covered'],
    ], dtype=object)

    moves = apply_logic_rules(board)
    assert isinstance(moves, list)


@pytest.mark.unit
def test_get_numbered_cells(sample_board):
    """Test getting all numbered cells from board."""
    from src.solver import get_numbered_cells

    numbered = get_numbered_cells(sample_board)

    assert len(numbered) == 2  # Two '1's in the sample board
    assert (1, 1) in numbered
    assert (1, 2) in numbered


@pytest.mark.unit
def test_get_unrevealed_neighbors(sample_board):
    """Test getting unrevealed neighbors of a cell."""
    from src.solver import get_unrevealed_neighbors

    unrevealed = get_unrevealed_neighbors(sample_board, 1, 1)

    # Cell (1,1) has value '1', check its neighbors
    assert isinstance(unrevealed, set)
    assert len(unrevealed) > 0


@pytest.mark.unit
def test_get_flagged_neighbors(sample_board):
    """Test getting flagged neighbors of a cell."""
    from src.solver import get_flagged_neighbors

    # Add a flag to the board
    board = sample_board.copy()
    board[2, 1] = 'flagged'

    flagged = get_flagged_neighbors(board, 1, 1)

    assert isinstance(flagged, set)


@pytest.mark.unit
def test_build_constraint_set(sample_board):
    """Test building constraint set from board."""
    from src.solver import build_constraint_set

    constraints = build_constraint_set(sample_board)

    assert isinstance(constraints, list)
    # Each constraint should be (set_of_cells, required_mine_count)
    for cells, count in constraints:
        assert isinstance(cells, set)
        assert isinstance(count, int)


@pytest.mark.unit
def test_calculate_probabilities():
    """Test probability calculation for covered cells."""
    from src.solver import calculate_probabilities

    # Simple board: 3x3 with one number '1' in center
    board = np.array([
        ['covered', 'covered', 'covered'],
        ['covered', '1', 'covered'],
        ['covered', 'covered', 'covered'],
    ], dtype=object)

    probabilities = calculate_probabilities(board)

    assert isinstance(probabilities, dict)
    # All covered cells should have probabilities
    assert len(probabilities) > 0

    # Check probabilities are in valid range
    for prob in probabilities.values():
        assert 0.0 <= prob <= 1.0


@pytest.mark.unit
def test_enumerate_valid_configurations():
    """Test enumeration of valid mine configurations."""
    from src.solver import enumerate_valid_configurations

    # Simple constraint: one cell group requiring 1 mine
    cells = {(0, 0), (0, 1)}
    constraints = [(cells, 1)]

    configs = enumerate_valid_configurations(constraints, max_iterations=100)

    assert isinstance(configs, list)
    assert len(configs) == 2  # Two ways to place 1 mine in 2 cells


@pytest.mark.unit
def test_solver_initialization():
    """Test Solver initialization."""
    from src.solver import MinesweeperSolver

    solver = MinesweeperSolver()
    assert solver.board is None


@pytest.mark.unit
def test_solver_solve_returns_moves():
    """Test that solve returns a list of moves."""
    from src.solver import MinesweeperSolver

    solver = MinesweeperSolver()

    # Simple board
    board = np.array([
        ['covered', 'covered'],
        ['covered', '1'],
    ], dtype=object)

    moves = solver.solve(board)

    assert isinstance(moves, list)
    # Each move should be ((row, col), action)
    for move in moves:
        assert isinstance(move, tuple)
        assert len(move) == 2
        assert isinstance(move[0], tuple)  # (row, col)
        assert move[1] in ['reveal', 'flag']


@pytest.mark.unit
def test_solver_update_board():
    """Test updating solver's board state."""
    from src.solver import MinesweeperSolver

    solver = MinesweeperSolver()
    board = np.array([['covered']], dtype=object)

    solver.solve(board)
    solver.update_board(0, 0, 'uncovered')

    assert solver.board[0, 0] == 'uncovered'


@pytest.mark.unit
def test_get_safest_cell():
    """Test finding the safest cell to click."""
    from src.solver import get_safest_cell

    probabilities = {
        (0, 0): 0.8,
        (0, 1): 0.2,
        (1, 0): 0.5,
    }

    safest = get_safest_cell(probabilities)

    assert safest == (0, 1)  # Lowest probability


@pytest.mark.unit
def test_get_cell_value():
    """Test extracting numeric value from numbered cell."""
    from src.solver import get_cell_value

    assert get_cell_value('1') == 1
    assert get_cell_value('8') == 8

    # Non-numbered cells should return 0
    assert get_cell_value('covered') == 0
    assert get_cell_value('uncovered') == 0
    assert get_cell_value('flagged') == 0


@pytest.mark.unit
def test_is_numbered_cell():
    """Test checking if a cell contains a number."""
    from src.solver import is_numbered_cell

    assert is_numbered_cell('1') is True
    assert is_numbered_cell('8') is True
    assert is_numbered_cell('covered') is False
    assert is_numbered_cell('uncovered') is False
    assert is_numbered_cell('flagged') is False
