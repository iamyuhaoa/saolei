"""Main game loop for autonomous Minesweeper AI."""

import logging
import time
from typing import Optional

import numpy as np

from src.config import config
from src.window_manager import WindowManager, WindowNotFoundError
from src.board_manager import BoardReader
from src.solver import MinesweeperSolver
from src.mouse_controller import MouseController

logger = logging.getLogger(__name__)


class MinesweeperBot:
    """Autonomous Minesweeper AI bot."""

    def __init__(self) -> None:
        """Initialize the bot."""
        self.window_manager: Optional[WindowManager] = None
        self.board_reader: Optional[BoardReader] = None
        self.solver: Optional[MinesweeperSolver] = None
        self.mouse_controller: Optional[MouseController] = None
        self.game_over: bool = False
        self.win: bool = False
        self.move_count: int = 0
        self.max_moves: int = 1000  # Safety limit

    def initialize(self) -> bool:
        """
        Initialize the bot and connect to Minesweeper window.

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing Minesweeper AI Bot...")

        # Initialize window manager
        self.window_manager = WindowManager()
        if not self.window_manager.connect():
            logger.error("Failed to connect to Minesweeper window")
            return False

        logger.info(f"Connected to window: {self.window_manager.window_rect}")

        # Initialize board reader
        self.board_reader = BoardReader()
        window_image = self.window_manager.capture()
        if not self.board_reader.initialize(window_image):
            logger.error("Failed to initialize board reader")
            return False

        logger.info(f"Board size: {self.board_reader.rows}x{self.board_reader.cols}")

        # Initialize solver
        self.solver = MinesweeperSolver()

        # Initialize mouse controller
        self.mouse_controller = MouseController(
            window_hwnd=self.window_manager.window_hwnd,
            window_rect=self.window_manager.window_rect,
            enable_safety=config.ENABLE_SAFETY,
            min_action_delay=config.ACTION_DELAY
        )

        logger.info("Initialization complete")
        return True

    def make_first_move(self) -> None:
        """Make initial move to start the game (click on corner)."""
        logger.info("Making first move...")

        # Click on top-left corner (usually safe)
        row, col = 0, 0
        self.mouse_controller.reveal_cell(
            row=row,
            col=col,
            grid_origin=self.board_reader.grid_origin,
            cell_size=self.board_reader.cell_size
        )
        self.move_count += 1

        # Wait for board to update
        time.sleep(0.3)

    def check_game_over(self, board: np.ndarray) -> bool:
        """
        Check if game is over (mine exploded).

        Args:
            board: Current board state

        Returns:
            True if game over, False otherwise
        """
        return config.STATE_MINE in board

    def check_win(self, board: np.ndarray) -> bool:
        """
        Check if game is won.

        Args:
            board: Current board state

        Returns:
            True if won, False otherwise
        """
        # Win if no covered cells remain
        covered_count = np.count_nonzero(board == config.STATE_COVERED)
        return covered_count == 0

    def execute_moves(self, moves: list) -> None:
        """
        Execute a list of moves.

        Args:
            moves: List of ((row, col), action) tuples
        """
        for (row, col), action in moves:
            if action == 'reveal':
                logger.debug(f"Revealing cell ({row}, {col})")
                self.mouse_controller.reveal_cell(
                    row=row,
                    col=col,
                    grid_origin=self.board_reader.grid_origin,
                    cell_size=self.board_reader.cell_size
                )
            elif action == 'flag':
                logger.debug(f"Flagging cell ({row}, {col})")
                self.mouse_controller.flag_cell(
                    row=row,
                    col=col,
                    grid_origin=self.board_reader.grid_origin,
                    cell_size=self.board_reader.cell_size
                )

            self.move_count += 1

            # Small delay between moves
            time.sleep(config.ACTION_DELAY)

    def run(self) -> bool:
        """
        Main game loop.

        Returns:
            True if won, False if lost or error
        """
        logger.info("Starting game loop...")

        try:
            # Make first move
            self.make_first_move()

            while not self.game_over and not self.win and self.move_count < self.max_moves:
                # Read current board state
                window_image = self.window_manager.capture()
                board = self.board_reader.read_board(window_image)

                # Check for game over or win
                if self.check_game_over(board):
                    logger.info("Game over - mine exploded!")
                    self.game_over = True
                    return False

                if self.check_win(board):
                    logger.info("You won!")
                    self.win = True
                    return True

                # Calculate next moves
                moves = self.solver.solve(board)

                if not moves:
                    logger.warning("No moves available - game may be stuck")
                    break

                # Execute moves
                logger.info(f"Executing {len(moves)} move(s)...")
                self.execute_moves(moves)

                # Small delay to let game update
                time.sleep(0.1)

            if self.move_count >= self.max_moves:
                logger.warning(f"Reached maximum move limit ({self.max_moves})")

            return self.win

        except WindowNotFoundError:
            logger.error("Lost connection to game window")
            return False
        except Exception as e:
            logger.error(f"Error during game loop: {e}")
            return False


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler("minesweeper_ai.log"),
            logging.StreamHandler()
        ]
    )


def main() -> int:
    """
    Main entry point.

    Returns:
        0 if success, 1 if error
    """
    setup_logging()
    logger.info("=" * 60)
    logger.info("Minesweeper AI Bot - Starting")
    logger.info("=" * 60)

    try:
        bot = MinesweeperBot()

        if not bot.initialize():
            logger.error("Initialization failed")
            return 1

        result = bot.run()

        if result:
            logger.info("Game won!")
            return 0
        else:
            logger.info("Game lost or failed")
            return 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
