"""Logging configuration for the calculator application."""

import logging
from pathlib import Path


class Logger:
    """Configures and provides a logger that writes to a file and the console."""

    def __init__(self, log_dir: Path, log_file: str = "calculator.log",
                 encoding: str = "utf-8", name: str = "calculator"):
        """Create the log directory and configure a named logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / log_file
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # LBYL: replace existing handlers when this logger was previously
        # configured for a different file, which happens when tests reuse a name
        existing = [h for h in self.logger.handlers
                    if getattr(h, "baseFilename", None) == str(self.log_path.resolve())]
        if not existing:
            for handler in list(self.logger.handlers):
                self.logger.removeHandler(handler)
                handler.close()
            handler = logging.FileHandler(self.log_path, encoding=encoding)
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        """Record an informational message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Record a warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Record an error message."""
        self.logger.error(message)