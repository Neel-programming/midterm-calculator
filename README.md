# Advanced Calculator

A modular command-line calculator built in Python using five design patterns, pandas-backed history, file logging, and environment-based configuration. Tested with pytest at 100% coverage, enforced by GitHub Actions.

## Features

- Ten operations: add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff
- REPL interface with color-coded output
- Commands: `history`, `clear`, `undo`, `redo`, `save`, `load`, `help`, `exit`
- Calculation history stored in a pandas DataFrame and persisted to CSV
- Auto-save after each calculation, configurable via environment variables
- Undo and redo across the full session
- File logging with INFO, WARNING, and ERROR levels
- Custom exception hierarchy with graceful error messages

## Design Patterns

| Pattern | Where | What it does |
|---|---|---|
| **Strategy** | `operations.py` | Each operation is an interchangeable class implementing `execute()` |
| **Factory** | `OperationFactory` | Creates the right operation strategy from the user's input |
| **Observer** | `history.py` | `LoggingObserver` and `AutoSaveObserver` react to each new calculation |
| **Memento** | `calculator_memento.py` | Snapshots of history power undo and redo |
| **Facade** | `Calculator` | A single class hiding config, operations, history, logging, and undo |

### Error handling paradigms

**LBYL (Look Before You Leap)** is used where a condition is cheap to check up front: the factory verifies an operation exists before creating it, division and modulus check their divisors, and the history manager checks a file exists before reading it.

**EAFP (Easier to Ask Forgiveness than Permission)** is used where checking first would duplicate the work: input conversion attempts `float()` and handles the failure, and file operations attempt the read or write and catch `OSError`.

## Project Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── calculator.py          Calculator facade and REPL loop
│   ├── calculation.py         Calculation records and CSV serialization
│   ├── calculator_config.py   Environment-based configuration
│   ├── calculator_memento.py  Memento and caretaker for undo/redo
│   ├── exceptions.py          Custom exception hierarchy
│   ├── history.py             Observers and pandas history manager
│   ├── input_validators.py    Input validation helpers
│   ├── logger.py              File logging configuration
│   └── operations.py          Operation strategies and factory
├── tests/                     One test module per app module
├── .env                       Configuration values
├── requirements.txt           Dependencies
├── README.md
└── .github/
    └── workflows/
        └── python-app.yml     CI: tests and 90% coverage gate
```

## Installation

```bash
git clone https://github.com/Neel-programming/midterm-calculator.git
cd midterm-calculator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Settings are read from a `.env` file in the project root:

| Variable | Default | Purpose |
|---|---|---|
| `CALCULATOR_LOG_DIR` | `./logs` | Directory for log files |
| `CALCULATOR_HISTORY_DIR` | `./history` | Directory for history files |
| `CALCULATOR_LOG_FILE` | `calculator.log` | Log filename |
| `CALCULATOR_HISTORY_FILE` | `history.csv` | History filename |
| `CALCULATOR_MAX_HISTORY_SIZE` | `100` | Maximum calculations kept in memory |
| `CALCULATOR_AUTO_SAVE` | `true` | Save after every calculation |
| `CALCULATOR_PRECISION` | `10` | Decimal places in results |
| `CALCULATOR_MAX_INPUT_VALUE` | `1000000000000` | Largest accepted operand |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Encoding for file operations |

Missing variables fall back to these defaults. Invalid values raise a `ConfigurationError` on startup.

### Logging

Logs are written to `CALCULATOR_LOG_DIR/CALCULATOR_LOG_FILE` with timestamps and severity levels. Every calculation, undo, redo, save, and error is recorded.

## Usage

```bash
python3 main.py
```

| Input | Output |
|---|---|
| `add 2 3` | `Result: 5.0` |
| `power 2 10` | `Result: 1024.0` |
| `modulus 10 3` | `Result: 1.0` |
| `int_divide 17 5` | `Result: 3.0` |
| `percent 25 200` | `Result: 12.5` |
| `abs_diff 3 10` | `Result: 7.0` |
| `divide 5 0` | `Division by zero is not allowed.` |
| `history` | Lists every calculation this session |
| `undo` | `Undone.` |
| `save` | `History saved.` |
| `help` | Command menu, generated from registered operations |

## Testing

```bash
pytest --cov=app --cov-report=term-missing
```

The suite has 144 tests across 8 modules at 100% coverage.

## Continuous Integration

GitHub Actions runs the test suite on every push and pull request to `main`. The build fails if any test fails or if coverage drops below 90%.

## Optional Feature

Color-coded output using `colorama`. Results print in green, errors in red, prompts in yellow, and headings in cyan.