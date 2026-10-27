"""Configuration management using environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


class CalculatorConfig:
    """Application settings loaded from environment variables."""

    def __init__(self, base_dir: Path = None):
        """Load settings from the environment and validate them."""
        self.base_dir = base_dir or Path(os.getenv("CALCULATOR_BASE_DIR", "./data"))
        self.history_file = self.base_dir / os.getenv("CALCULATOR_HISTORY_FILE", "history.csv")
        self.max_history_size = self._read_int("CALCULATOR_MAX_HISTORY_SIZE", 100)
        self.precision = self._read_int("CALCULATOR_PRECISION", 10)
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

    def validate(self) -> None:
        """Raise ConfigurationError if any setting is out of range."""
        # LBYL: check the values before the application relies on them
        if self.max_history_size <= 0:
            raise ConfigurationError("Max history size must be positive.")
        if self.precision < 0:
            raise ConfigurationError("Precision cannot be negative.")