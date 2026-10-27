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
    """Observer that writes each calculation to the application log."""

    def __init__(self, logger):
        """Store the logger to write through."""
        self.logger = logger

    def update(self, calculation: Calculation) -> None:
        """Log the operation, operands, and result of a calculation."""