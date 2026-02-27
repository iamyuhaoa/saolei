"""Window detection and management for Minesweeper."""

import logging
import sys
from typing import Optional, Tuple

import cv2
import numpy as np

from src.config import config

logger = logging.getLogger(__name__)

# Check if running on Windows
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import win32con
    import win32gui
    import win32ui
    from pywinauto import findwindows
else:
    # Mock imports for non-Windows platforms (for testing)
    class MockModule:
        """Mock module for non-Windows platforms."""

    win32con = MockModule()
    win32gui = MockModule()
    win32ui = MockModule()
    findwindows = MockModule()


class WindowNotFoundError(Exception):
    """Raised when Minesweeper window is not found."""


def find_minesweeper_window() -> Optional[int]:
    """
    Find the Minesweeper window.
    Supports multiple Minesweeper versions (Windows 7, 10, 11).

    Returns:
        Window handle (hwnd) or None if not found.
    """
    if not IS_WINDOWS:
        return None

    # Try different window class names for different Minesweeper versions
    for class_name in config.WINDOW_CLASS_PRIORITY:
        try:
            handles = findwindows.find_elements(class_name=class_name)
            if handles:
                return handles[0].handle
        except Exception as e:
            logger.debug(f"Failed to find window with class '{class_name}': {e}")
            continue

    # Fallback: search by title pattern
    try:
        handles = findwindows.find_elements(title_re=config.WINDOW_TITLE_PATTERN)
        if handles:
            return handles[0].handle
    except Exception as e:
        logger.debug(f"Failed to find window by title pattern: {e}")

    return None


def capture_window(hwnd: int) -> np.ndarray:
    """
    Capture the Minesweeper window content.

    Args:
        hwnd: Window handle

    Returns:
        numpy array (BGR image) of the window content

    Raises:
        RuntimeError: If capture fails
        NotImplementedError: If not running on Windows
    """
    if not IS_WINDOWS:
        raise NotImplementedError("Window capture is only supported on Windows")

    # Initialize GDI resources to None for finally block
    hwndDC = None
    mfcDC = None
    saveDC = None
    saveBitMap = None

    try:
        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Create device context
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # Create bitmap
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # BitBlt screenshot
        result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        # Convert to numpy array
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        img.shape = (height, width, 4)

        # Convert BGRA to BGR
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img_bgr

    except Exception as e:
        raise RuntimeError(f"Failed to capture window: {e}")
    finally:
        # Ensure GDI resources are cleaned up
        if saveDC:
            saveDC.DeleteDC()
        if mfcDC:
            mfcDC.DeleteDC()
        if hwndDC:
            win32gui.ReleaseDC(hwnd, hwndDC)
        if saveBitMap:
            saveBitMap.DeleteObject()


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """
    Get window rectangle coordinates.

    Args:
        hwnd: Window handle

    Returns:
        Tuple of (left, top, right, bottom)
    """
    if not IS_WINDOWS:
        return (0, 0, 100, 100)

    return win32gui.GetWindowRect(hwnd)


def get_window_text(hwnd: int) -> str:
    """
    Get window title text.

    Args:
        hwnd: Window handle

    Returns:
        Window title string
    """
    if not IS_WINDOWS:
        return "Mock Window"

    return win32gui.GetWindowText(hwnd)


class WindowManager:
    """Manages Minesweeper window detection and connection."""

    def __init__(self) -> None:
        """Initialize WindowManager."""
        self.window_hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None

    def connect(self) -> bool:
        """
        Connect to Minesweeper window.

        Returns:
            True if connection successful, False otherwise
        """
        if not IS_WINDOWS:
            return False

        self.window_hwnd = find_minesweeper_window()

        if self.window_hwnd is None:
            return False

        try:
            self.window_rect = get_window_rect(self.window_hwnd)
            return True
        except Exception as e:
            logger.debug(f"Failed to get window rect: {e}")
            self.window_hwnd = None
            return False

    def capture(self) -> np.ndarray:
        """
        Capture the current window content.

        Returns:
            BGR image as numpy array

        Raises:
            WindowNotFoundError: If no window is connected
        """
        if self.window_hwnd is None:
            raise WindowNotFoundError("No window connected. Call connect() first.")

        return capture_window(self.window_hwnd)

    def is_connected(self) -> bool:
        """Check if currently connected to a window."""
        return self.window_hwnd is not None

    def reconnect(self) -> bool:
        """
        Attempt to reconnect to the window.

        Returns:
            True if reconnection successful, False otherwise
        """
        return self.connect()
