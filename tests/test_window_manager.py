"""Tests for window manager module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np


@pytest.fixture
def mock_windows_env():
    """Mock Windows environment for testing."""
    with patch("src.window_manager.IS_WINDOWS", True):
        with (
            patch("src.window_manager.win32gui") as mock_gui,
            patch("src.window_manager.win32ui") as mock_ui,
            patch("src.window_manager.win32con") as mock_con,
            patch("src.window_manager.findwindows") as mock_find,
        ):
            yield {"gui": mock_gui, "ui": mock_ui, "con": mock_con, "find": mock_find}


@pytest.mark.unit
def test_find_minesweeper_window_exists(mock_windows_env):
    """Test finding Minesweeper window when it exists."""
    # Import after mocking IS_WINDOWS
    from src.window_manager import find_minesweeper_window

    mock_find = mock_windows_env["find"]

    # Mock window handle
    mock_handle = Mock()
    mock_handle.handle = 12345
    mock_find.find_elements.return_value = [mock_handle]

    result = find_minesweeper_window()
    assert result is not None
    assert result == 12345


@pytest.mark.unit
def test_find_minesweeper_window_not_found(mock_windows_env):
    """Test finding Minesweeper window when it doesn't exist."""
    from src.window_manager import find_minesweeper_window

    mock_find = mock_windows_env["find"]

    mock_find.find_elements.return_value = []

    result = find_minesweeper_window()
    assert result is None


@pytest.mark.unit
def test_capture_window_returns_numpy_array(mock_windows_env):
    """Test that window capture uses correct Windows API calls."""
    from src.window_manager import capture_window

    mock_gui = mock_windows_env["gui"]
    mock_ui = mock_windows_env["ui"]
    mock_con = mock_windows_env["con"]

    # Setup mocks
    mock_gui.GetWindowRect.return_value = (100, 100, 500, 600)
    mock_gui.GetWindowDC.return_value = "hwndDC"

    mock_dc = MagicMock()
    mock_ui.CreateDCFromHandle.return_value = mock_dc
    mock_ui.CreateCompatibleBitmap.return_value = mock_dc
    mock_ui.CreateBitmap.return_value = MagicMock()

    # Mock bitmap data
    bitmap_data = b"\x00" * (500 * 400 * 4)  # Fake BGRA data

    with (
        patch("src.window_manager.cv2") as mock_cv2,
        patch(
            "src.window_manager.np.frombuffer",
            return_value=np.zeros((500 * 400 * 4,), dtype=np.uint8),
        ),
    ):
        mock_img = np.zeros((500, 400, 3), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = mock_img

        result = capture_window(12345)
        assert isinstance(result, np.ndarray)
        # Verify Windows API calls were made
        mock_gui.GetWindowRect.assert_called_once()
        mock_gui.GetWindowDC.assert_called_once()


@pytest.mark.unit
def test_capture_window_not_on_windows():
    """Test that capture_window raises NotImplementedError on non-Windows."""
    from src.window_manager import capture_window, IS_WINDOWS

    # Ensure we're testing on non-Windows
    if not IS_WINDOWS:
        with pytest.raises(NotImplementedError):
            capture_window(12345)


@pytest.mark.unit
def test_get_window_rect(mock_windows_env):
    """Test getting window rectangle."""
    from src.window_manager import get_window_rect

    mock_gui = mock_windows_env["gui"]

    mock_gui.GetWindowRect.return_value = (100, 100, 500, 600)

    rect = get_window_rect(12345)
    assert rect == (100, 100, 500, 600)
    assert rect[2] - rect[0] == 400  # width
    assert rect[3] - rect[1] == 500  # height


@pytest.mark.unit
def test_get_window_rect_non_windows():
    """Test getting window rect on non-Windows returns default."""
    from src.window_manager import get_window_rect, IS_WINDOWS

    if not IS_WINDOWS:
        rect = get_window_rect(12345)
        assert rect == (0, 0, 100, 100)


@pytest.mark.unit
def test_window_manager_initialization():
    """Test WindowManager initialization."""
    from src.window_manager import WindowManager

    manager = WindowManager()
    assert manager.window_hwnd is None
    assert manager.window_rect is None


@pytest.mark.unit
def test_window_manager_connect(mock_windows_env):
    """Test WindowManager connecting to a window."""
    from src.window_manager import WindowManager

    mock_find = mock_windows_env["find"]
    mock_gui = mock_windows_env["gui"]

    manager = WindowManager()

    # Mock successful find
    mock_handle = Mock()
    mock_handle.handle = 12345
    mock_find.find_elements.return_value = [mock_handle]

    mock_gui.GetWindowText.return_value = "Minesweeper"
    mock_gui.GetWindowRect.return_value = (100, 100, 500, 600)

    result = manager.connect()
    assert result is True
    assert manager.window_hwnd == 12345
    assert manager.window_rect == (100, 100, 500, 600)


@pytest.mark.unit
def test_window_manager_connect_fails():
    """Test WindowManager connection failure."""
    from src.window_manager import WindowManager, IS_WINDOWS

    manager = WindowManager()

    # On non-Windows, should fail immediately
    if not IS_WINDOWS:
        result = manager.connect()
        assert result is False
    else:
        # On Windows with no window found
        with patch("src.window_manager.find_minesweeper_window", return_value=None):
            result = manager.connect()
            assert result is False


@pytest.mark.unit
def test_window_manager_is_connected():
    """Test is_connected method."""
    from src.window_manager import WindowManager

    manager = WindowManager()
    assert manager.is_connected() is False

    manager.window_hwnd = 12345
    assert manager.is_connected() is True


@pytest.mark.unit
def test_window_manager_capture_not_connected():
    """Test capture raises error when not connected."""
    from src.window_manager import WindowManager, WindowNotFoundError

    manager = WindowManager()

    with pytest.raises(WindowNotFoundError):
        manager.capture()


@pytest.mark.unit
def test_window_manager_reconnect(mock_windows_env):
    """Test reconnect method."""
    from src.window_manager import WindowManager

    mock_find = mock_windows_env["find"]
    mock_gui = mock_windows_env["gui"]

    manager = WindowManager()

    # First connection
    mock_handle = Mock()
    mock_handle.handle = 12345
    mock_find.find_elements.return_value = [mock_handle]
    mock_gui.GetWindowRect.return_value = (100, 100, 500, 600)

    result1 = manager.connect()
    assert result1 is True

    # Disconnect
    manager.window_hwnd = None

    # Reconnect
    result2 = manager.reconnect()
    assert result2 is True
    assert manager.window_hwnd == 12345
