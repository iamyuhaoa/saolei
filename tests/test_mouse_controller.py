"""Tests for mouse controller module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


@pytest.fixture
def mock_mouse():
    """Mock pywinauto mouse."""
    mock_mouse = MagicMock()
    return mock_mouse


@pytest.mark.unit
def test_mouse_controller_initialization():
    """Test MouseController initialization."""
    from src.mouse_controller import MouseController

    controller = MouseController(window_hwnd=12345, window_rect=(100, 100, 500, 500))

    assert controller.window_hwnd == 12345
    assert controller.window_rect == (100, 100, 500, 500)


@pytest.mark.unit
def test_cell_to_screen_coordinates():
    """Test conversion from cell to screen coordinates."""
    from src.mouse_controller import MouseController

    controller = MouseController(window_hwnd=12345, window_rect=(100, 100, 500, 500))

    screen_x, screen_y = controller._cell_to_screen_coords(
        row=1, col=2, grid_origin=(10, 10), cell_size=(30, 30)
    )

    # origin_x + col * width + half_width
    # 100 + 10 + 2 * 30 + 15 = 185
    assert screen_x == 185
    assert screen_y == 155  # 100 + 10 + 1 * 30 + 15


@pytest.mark.unit
def test_click_cell_left(mock_mouse):
    """Test left clicking on a cell."""
    from src.mouse_controller import MouseController

    controller = MouseController(
        window_hwnd=12345,
        window_rect=(100, 100, 500, 500),
        enable_safety=False,  # Disable safety to avoid time.time() issues in tests
    )

    with (
        patch("src.mouse_controller.mouse", mock_mouse),
        patch("src.mouse_controller.IS_WINDOWS", True),
    ):
        controller.click_cell(
            row=1, col=1, grid_origin=(10, 10), cell_size=(30, 30), button="left"
        )

    # Verify mouse.move and click were called
    assert mock_mouse.move.called
    assert mock_mouse.click.called


@pytest.mark.unit
def test_click_cell_right(mock_mouse):
    """Test right clicking on a cell."""
    from src.mouse_controller import MouseController

    controller = MouseController(window_hwnd=12345, window_rect=(100, 100, 500, 500))

    with (
        patch("src.mouse_controller.mouse", mock_mouse),
        patch("src.mouse_controller.IS_WINDOWS", True),
    ):
        import time

        controller.click_cell(
            row=0, col=0, grid_origin=(10, 10), cell_size=(30, 30), button="right"
        )

    assert mock_mouse.click.called


@pytest.mark.unit
def test_reveal_cell(mock_mouse):
    """Test revealing a cell."""
    from src.mouse_controller import MouseController

    controller = MouseController(window_hwnd=12345, window_rect=(100, 100, 500, 500))

    with (
        patch("src.mouse_controller.mouse", mock_mouse),
        patch("src.mouse_controller.IS_WINDOWS", True),
    ):
        controller.reveal_cell(row=2, col=3, grid_origin=(10, 10), cell_size=(30, 30))

    # Should call click with 'left' button
    assert mock_mouse.click.called


@pytest.mark.unit
def test_flag_cell(mock_mouse):
    """Test flagging a cell."""
    from src.mouse_controller import MouseController

    controller = MouseController(window_hwnd=12345, window_rect=(100, 100, 500, 500))

    with (
        patch("src.mouse_controller.mouse", mock_mouse),
        patch("src.mouse_controller.IS_WINDOWS", True),
    ):
        controller.flag_cell(row=1, col=1, grid_origin=(10, 10), cell_size=(30, 30))

    # Should call click with 'right' button
    assert mock_mouse.click.called


@pytest.mark.unit
def test_not_on_windows():
    """Test behavior on non-Windows platform."""
    from src.mouse_controller import MouseController, IS_WINDOWS

    if not IS_WINDOWS:
        controller = MouseController(
            window_hwnd=12345, window_rect=(100, 100, 500, 500)
        )

        with pytest.raises(NotImplementedError):
            controller.click_cell(0, 0, (10, 10), (30, 30), "left")


@pytest.mark.unit
def test_invalid_button(mock_mouse):
    """Test that invalid button raises error."""
    from src.mouse_controller import MouseController

    controller = MouseController(
        window_hwnd=12345, window_rect=(100, 100, 500, 500), enable_safety=False
    )

    with (
        patch("src.mouse_controller.mouse", mock_mouse),
        patch("src.mouse_controller.IS_WINDOWS", True),
        pytest.raises(ValueError),
    ):
        controller.click_cell(0, 0, (10, 10), (30, 30), "invalid")
