"""Tests for main game loop."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
def test_bot_initialization():
    """Test MinesweeperBot initialization."""
    from src.main import MinesweeperBot

    bot = MinesweeperBot()

    assert bot.window_manager is None
    assert bot.board_reader is None
    assert bot.solver is None
    assert bot.mouse_controller is None
    assert bot.game_over is False
    assert bot.win is False


@pytest.mark.unit
def test_check_game_over():
    """Test game over detection."""
    from src.main import MinesweeperBot
    from src.config import config

    bot = MinesweeperBot()

    # Board with mine
    board = np.array([['mine']], dtype=object)
    assert bot.check_game_over(board) is True

    # Board without mine
    board = np.array([[config.STATE_COVERED]], dtype=object)
    assert bot.check_game_over(board) is False


@pytest.mark.unit
def test_check_win():
    """Test win detection."""
    from src.main import MinesweeperBot
    from src.config import config

    bot = MinesweeperBot()

    # Board with no covered cells - win
    board = np.array([[config.STATE_UNCOVERED]], dtype=object)
    assert bot.check_win(board) is True

    # Board with covered cells - not win
    board = np.array([[config.STATE_COVERED]], dtype=object)
    assert bot.check_win(board) is False


@pytest.mark.unit
def test_execute_moves_reveal():
    """Test executing reveal moves."""
    from src.main import MinesweeperBot

    bot = MinesweeperBot()
    bot.mouse_controller = MagicMock()
    bot.board_reader = MagicMock()
    bot.board_reader.grid_origin = (10, 10)
    bot.board_reader.cell_size = (30, 30)

    moves = [((0, 0), 'reveal'), ((1, 1), 'flag')]

    with patch('src.main.time'):
        bot.execute_moves(moves)

    assert bot.mouse_controller.reveal_cell.called
    assert bot.mouse_controller.flag_cell.called


@pytest.mark.unit
def test_check_game_over_false():
    """Test game over detection returns False when no mine."""
    from src.main import MinesweeperBot
    from src.config import config

    bot = MinesweeperBot()
    board = np.array([
        [config.STATE_COVERED, config.STATE_UNCOVERED],
        [config.STATE_FLAGGED, config.STATE_UNCOVERED]
    ], dtype=object)

    result = bot.check_game_over(board)
    assert result is False


@pytest.mark.unit
def test_check_win_multiple_covered():
    """Test win detection with multiple covered cells remaining."""
    from src.main import MinesweeperBot
    from src.config import config

    bot = MinesweeperBot()
    board = np.array([
        [config.STATE_COVERED, config.STATE_UNCOVERED],
        [config.STATE_UNCOVERED, config.STATE_UNCOVERED]
    ], dtype=object)

    result = bot.check_win(board)
    assert result is False


@pytest.mark.unit
def test_make_first_move():
    """Test first move initialization."""
    from src.main import MinesweeperBot

    bot = MinesweeperBot()
    bot.mouse_controller = MagicMock()
    bot.board_reader = MagicMock()
    bot.board_reader.grid_origin = (10, 10)
    bot.board_reader.cell_size = (30, 30)

    with patch('src.main.time'):
        bot.make_first_move()

    # Should click corner (0, 0)
    bot.mouse_controller.reveal_cell.assert_called_once()
    assert bot.move_count == 1


@pytest.mark.unit
def test_setup_logging():
    """Test logging setup."""
    from src.main import setup_logging
    import logging

    setup_logging()

    # Check that root logger has handlers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0


@pytest.mark.unit
def test_main_returns_zero_on_win():
    """Test main function returns 0 on win."""
    from src.main import main

    with patch('src.main.MinesweeperBot') as mock_bot_class:
        mock_bot = MagicMock()
        mock_bot.initialize.return_value = True
        mock_bot.run.return_value = True  # Win
        mock_bot_class.return_value = mock_bot

        result = main()
        assert result == 0


@pytest.mark.unit
def test_main_returns_one_on_loss():
    """Test main function returns 1 on loss."""
    from src.main import main

    with patch('src.main.MinesweeperBot') as mock_bot_class:
        mock_bot = MagicMock()
        mock_bot.initialize.return_value = True
        mock_bot.run.return_value = False  # Loss
        mock_bot_class.return_value = mock_bot

        result = main()
        assert result == 1


@pytest.mark.unit
def test_main_returns_one_on_init_failure():
    """Test main function returns 1 on initialization failure."""
    from src.main import main

    with patch('src.main.MinesweeperBot') as mock_bot_class:
        mock_bot = MagicMock()
        mock_bot.initialize.return_value = False
        mock_bot_class.return_value = mock_bot

        result = main()
        assert result == 1
