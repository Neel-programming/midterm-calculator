"""Configuration management using environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


class CalculatorConfig:
    """Application settings loaded from environment variables."""

    def __init__(self, log_dir: Path = None, history_dir: Path = None):
        """Load settings from the environment and validate them."""
        self.log_dir = Path(log_dir or os.getenv("CALCULATOR_LOG_DIR", "./logs"))
        self.history_dir = Path(history_dir or os.getenv("CALCULATOR_HISTORY_DIR", "./history"))
        self.log_file = self.log_dir / os.getenv("CALCULATOR_LOG_FILE", "calculator.log")
        self.history_file = self.history_dir / os.getenv("CALCULATOR_HISTORY_FILE", "history.csv")
        self.max_history_size = self._read_int("CALCULATOR_MAX_HISTORY_SIZE", 100)
        self.precision = self._read_int("CALCULATOR_PRECISION", 10)
        self.max_input_value = self._read_float("CALCULATOR_MAX_INPUT_VALUE", 1e12)
        self.default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
        self.auto_save = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() == "true"
        self.validate()

    @staticmethod
    def _read_int(name: str, default: int) -> int:
        """Read an integer setting, falling back to a default."""
        # EAFP: attempt the conversion and handle a bad value if it occurs
        try:
            return int(os.getenv(name, default))
        except ValueError as error:
            raise ConfigurationError(f"{name} must be an integer.") from error

    @staticmethod
    def _read_float(name: str, default: float) -> float:
        """Read a float setting, falling back to a default."""
        # EAFP: attempt the conversion and handle a bad value if it occurs
        try:
            return float(os.getenv(name, default))
        except ValueError as error:
            raise ConfigurationError(f"{name} must be a number.") from error

    def validate(self) -> None:
        """Raise ConfigurationError if any setting is out of range."""
        # LBYL: check the values before the application relies on them
        if self.max_history_size <= 0:
            raise ConfigurationError("Max history size must be positive.")
        if self.precision < 0:
            raise ConfigurationError("Precision cannot be negative.")
        if self.max_input_value <= 0:
            raise ConfigurationError("Max input value must be positive.")