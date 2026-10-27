"""Memento pattern for undo and redo support."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CalculatorMemento:
    """A snapshot of the calculator's history at a point in time."""

    history: list
    timestamp: datetime = field(default_factory=datetime.now)

    def restore(self) -> list:
        """Return a copy of the saved history."""
        return list(self.history)


class Caretaker:
    """Stores mementos and manages undo and redo stacks."""

    def __init__(self):
        """Start with empty undo and redo stacks."""
        self._undo_stack = []
        self._redo_stack = []

    def save(self, history: list) -> None:
        """Record the current history and clear the redo stack."""
        self._undo_stack.append(CalculatorMemento(list(history)))
        self._redo_stack.clear()

    def undo(self, current: list):
        """Return the previous history, or None if there is nothing to undo."""
        # LBYL: check the stack before attempting to pop from it
        if not self._undo_stack:
            return None
        self._redo_stack.append(CalculatorMemento(list(current)))
        return self._undo_stack.pop().restore()

    def redo(self, current: list):
        """Return the undone history, or None if there is nothing to redo."""
        if not self._redo_stack:
            return None
        self._undo_stack.append(CalculatorMemento(list(current)))
        return self._redo_stack.pop().restore()

    def clear(self) -> None:
        """Empty both stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()