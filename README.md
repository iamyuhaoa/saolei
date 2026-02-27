# Minesweeper AI Bot

An autonomous AI that plays Windows Minesweeper automatically.

## Features

- **Computer Vision**: Uses OpenCV to recognize the Minesweeper board state
- **Constraint Satisfaction**: Applies logical rules to solve deterministic situations
- **Probability Calculation**: Calculates optimal moves using constraint enumeration
- **Mouse Automation**: Uses pywinauto for precise mouse control
- **Standalone EXE**: Packaged as a single executable for easy deployment

## Requirements

- Windows 10/11
- Minesweeper game (Windows built-in or compatible version)

## Installation

### Option 1: Run from Source

1. Install Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python src/main.py
   ```

### Option 2: Use Standalone EXE

1. Download the latest `MinesweeperAI.exe` from the Releases section
2. Double-click to run (no Python installation required)

## Usage

1. Open Minesweeper on your computer
2. Run the bot:
   - **EXE**: Double-click `MinesweeperAI.exe`
   - **Source**: `python src/main.py`
3. The bot will automatically:
   - Detect the Minesweeper window
   - Read the board state
   - Calculate optimal moves
   - Play automatically

## Configuration

Edit `resources/config.json` to customize:

```json
{
  "solver": {
    "enable_logic_rules": true,
    "enable_probability_calculation": true,
    "max_configurations": 10000
  },
  "mouse": {
    "action_delay": 0.1,
    "enable_safety": true
  }
}
```

## Building from Source

To build the standalone EXE:

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller build.spec

# The EXE will be in dist/MinesweeperAI.exe
```

## Project Structure

```
saolei/
├── src/
│   ├── main.py              # Entry point and game loop
│   ├── config.py            # Configuration constants
│   ├── window_manager.py    # Window detection and capture
│   ├── board_manager.py     # Board state recognition
│   ├── solver.py            # AI solving algorithm
│   └── mouse_controller.py  # Mouse automation
├── resources/
│   └── config.json          # Runtime configuration
├── tests/                   # Unit tests
├── build.spec              # PyInstaller configuration
└── requirements.txt        # Python dependencies
```

## Algorithm

The bot uses a two-phase approach:

### Phase 1: Logic-Based Solving
- Applies standard Minesweeper deduction rules
- Finds guaranteed safe moves and mines
- Example: If a '1' cell has only 1 unrevealed neighbor, that neighbor is a mine

### Phase 2: Probability-Based Solving
- When no deterministic solution exists
- Enumerates all valid mine configurations
- Calculates probability for each cell
- Chooses the cell with lowest mine probability

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## License

MIT License

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting PRs.
