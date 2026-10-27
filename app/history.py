"""Observers and pandas-backed history management."""

from abc import ABC, abstractmethod

import pandas as pd

from app.calculation import Calculation
from app.exceptions import OperationError


class CalculationObserver(ABC):
    """Observer interface for reacting to completed calculations."""

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """React to a newly completed calculation."""


class LoggingObserver(CalculationObserver):
    """Observer that records each calculation in a log."""

    def __init__(self):
        """Start with an empty log."""
        self.entries = []

    def update(self, calculation: Calculation) -> None:
        """Append a readable record of the calculation."""
        self.entries.append(str(calculation))


class AutoSaveObserver(CalculationObserver):
    """Observer that saves history to disk after each calculation."""

    def __init__(self, manager: "HistoryManager"):
        """Remember the history manager to save through."""
        self.manager = manager

    def update(self, calculation: Calculation) -> None:
        """Save the history if auto-save is enabled."""
        if self.manager.config.auto_save:
            self.manager.save()


class HistoryManager:
    """Stores calculations and persists them with pandas."""

    COLUMNS = ["operation", "operand_a", "operand_b", "result", "timestamp"]

    def __init__(self, config):
        """Store the configuration and start with an empty history."""
        self.config = config
        self.history = []
        self._observers = []

    def attach(self, observer: CalculationObserver) -> None:
        """Register an observer to be notified of new calculations."""
        self._observers.append(observer)

    def notify(self, calculation: Calculation) -> None:
        """Notify every registered observer of a calculation."""
        for observer in self._observers:
            observer.update(calculation)

    def add(self, calculation: Calculation) -> None:
        """Add a calculation, trim to the configured size, and notify."""
        self.history.append(calculation)
        if len(self.history) > self.config.max_history_size:
            self.history = self.history[-self.config.max_history_size:]
        self.notify(calculation)

    def clear(self) -> None:
        """Remove every calculation from the history."""
        self.history = []

    def to_dataframe(self) -> pd.DataFrame:
        """Return the history as a pandas DataFrame."""
        if not self.history:
            return pd.DataFrame(columns=self.COLUMNS)
        return pd.DataFrame([calculation.to_dict() for calculation in self.history])

    def save(self) -> None:
        """Write the history to the configured CSV file."""
        # EAFP: attempt the write and report any filesystem failure
        try:
            self.config.base_dir.mkdir(parents=True, exist_ok=True)
            self.to_dataframe().to_csv(self.config.history_file, index=False)
        except OSError as error:
            raise OperationError(f"Could not save history: {error}") from error

    def load(self) -> pd.DataFrame:
        """Read the history CSV and return it as a DataFrame."""
        # LBYL: check the file exists before trying to read it
        if not self.config.history_file.exists():
            return pd.DataFrame(columns=self.COLUMNS)
        try:
            return pd.read_csv(self.config.history_file)
        except (OSError, pd.errors.ParserError) as error:
            raise OperationError(f"Could not load history: {error}") from error