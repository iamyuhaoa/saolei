"""Tests for board reader module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_window_manager():
    """Mock WindowManager."""
    with patch("src.board_manager.WindowManager") as mock:
        yield mock


@pytest.mark.unit
def test_detect_grid_structure_finds_uniform_cells():
    """Test grid detection on uniform cell pattern."""
    from src.board_manager import detect_grid_structure

    # Create test image with grid pattern
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    # Draw some grid-like pattern
    for i in range(0, 300, 30):
        img[i : i + 2, :] = 255  # Horizontal lines
        img[:, i : i + 2] = 255  # Vertical lines

    cell_size, origin = detect_grid_structure(img)

    assert cell_size is not None
    assert origin is not None
    assert isinstance(cell_size, tuple)
    assert len(cell_size) == 2


@pytest.mark.unit
def test_classify_cell_covered():
    """Test classification of covered cell."""
    from src.board_manager import classify_cell
    from src.config import config

    # Create gray image (covered cell color)
    gray_value = 190
    cell_img = np.full((20, 20, 3), gray_value, dtype=np.uint8)

    result = classify_cell(cell_img, config.get_color_thresholds())

    assert result == config.STATE_COVERED


@pytest.mark.unit
def test_classify_cell_flagged():
    """Test classification of flagged cell."""
    from src.board_manager import classify_cell
    from src.config import config

    # Create red image (flag color)
    cell_img = np.zeros((20, 20, 3), dtype=np.uint8)
    cell_img[:, :, 2] = 230  # Red channel (BGR)

    result = classify_cell(cell_img, config.get_color_thresholds())

    assert result == config.STATE_FLAGGED


@pytest.mark.unit
def test_classify_cell_number():
    """Test classification of numbered cell."""
    from src.board_manager import classify_cell
    from src.config import config

    # Create light background (uncovered) - use 220 which is above covered range
    # and has balanced channels (not high red like flag)
    cell_img = np.full((20, 20, 3), 220, dtype=np.uint8)
    # Reduce red channel slightly to avoid flag detection
    cell_img[:, :, 2] = 180  # BGR format, reduce red channel

    result = classify_cell(cell_img, config.get_color_thresholds())

    # Should be uncovered (light background, not high red)
    assert result == config.STATE_UNCOVERED


@pytest.mark.unit
def test_board_reader_initialization():
    """Test BoardReader initialization."""
    from src.board_manager import BoardReader

    reader = BoardReader()
    assert reader.cell_size is None
    assert reader.grid_origin is None
    assert reader.rows is None
    assert reader.cols is None


@pytest.mark.unit
def test_board_reader_initialize():
    """Test BoardReader initialization with image."""
    from src.board_manager import BoardReader

    reader = BoardReader()

    # Create test image
    img = np.zeros((300, 300, 3), dtype=np.uint8)

    with patch("src.board_manager.detect_grid_structure") as mock_detect:
        mock_detect.return_value = ((30, 30), (10, 10))

        reader.initialize(img)

        assert reader.cell_size == (30, 30)
        assert reader.grid_origin == (10, 10)


@pytest.mark.unit
def test_board_reader_read_board():
    """Test reading complete board."""
    from src.board_manager import BoardReader
    from src.config import config

    reader = BoardReader()
    reader.cell_size = (30, 30)
    reader.grid_origin = (10, 10)
    reader.rows = 9
    reader.cols = 9

    # Create test image (all covered - gray)
    img = np.full((300, 300, 3), 190, dtype=np.uint8)

    with patch("src.board_manager.classify_cell") as mock_classify:
        mock_classify.return_value = config.STATE_COVERED

        board = reader.read_board(img)

        assert board.shape == (9, 9)
        # All cells should be covered
        assert np.all(board == config.STATE_COVERED)


@pytest.mark.unit
def test_get_neighbors_corner():
    """Test getting neighbors for corner cell."""
    from src.board_manager import get_neighbors

    # Top-left corner (0, 0) on 9x9 board
    neighbors = get_neighbors(9, 9, 0, 0)

    # Should have 3 neighbors
    assert len(neighbors) == 3
    assert (0, 1) in neighbors
    assert (1, 0) in neighbors
    assert (1, 1) in neighbors


@pytest.mark.unit
def test_get_neighbors_center():
    """Test getting neighbors for center cell."""
    from src.board_manager import get_neighbors

    # Center cell (4, 4) on 9x9 board
    neighbors = get_neighbors(9, 9, 4, 4)

    # Should have 8 neighbors
    assert len(neighbors) == 8


@pytest.mark.unit
def test_get_neighbors_edge():
    """Test getting neighbors for edge cell."""
    from src.board_manager import get_neighbors

    # Top edge (0, 4) on 9x9 board
    neighbors = get_neighbors(9, 9, 0, 4)

    # Should have 5 neighbors
    assert len(neighbors) == 5


@pytest.mark.unit
def test_cell_coordinates_to_screen():
    """Test conversion from cell coordinates to screen coordinates."""
    from src.board_manager import cell_coordinates_to_screen

    screen_x, screen_y = cell_coordinates_to_screen(
        row=1,
        col=2,
        grid_origin=(100, 100),
        cell_size=(30, 30),
    )

    assert screen_x == 100 + 2 * 30 + 15  # origin_x + col * width + half_width
    assert screen_y == 100 + 1 * 30 + 15  # origin_y + row * height + half_height


@pytest.mark.unit
def test_screen_coordinates_to_cell():
    """Test conversion from screen coordinates to cell coordinates."""
    from src.board_manager import screen_coordinates_to_cell

    row, col = screen_coordinates_to_cell(
        screen_x=175,
        screen_y=145,
        grid_origin=(100, 100),
        cell_size=(30, 30),
    )

    # 175 - 100 = 75, 75 // 30 = 2
    # 145 - 100 = 45, 45 // 30 = 1
    assert col == 2
    assert row == 1


@pytest.mark.unit
def test_detect_board_size():
    """Test detecting board size from image."""
    from src.board_manager import detect_board_size

    # Create test image with grid
    img = np.zeros((500, 500, 3), dtype=np.uint8)

    with patch("src.board_manager.detect_grid_structure") as mock_detect:
        mock_detect.return_value = ((30, 30), (50, 50))

        rows, cols = detect_board_size(img, cell_size=(30, 30), grid_origin=(50, 50))

        # Should calculate based on image size and cell size
        assert isinstance(rows, int)
        assert isinstance(cols, int)
        assert rows > 0
        assert cols > 0
