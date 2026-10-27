"""Facade and REPL interface for the calculator application."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import Caretaker
from app.exceptions import CalculatorError
from app.history import AutoSaveObserver, HistoryManager, LoggingObserver
from app.input_validators import validate_operands
from app.operations import OperationFactory

MENU = """
Available commands:
  add <a> <b>        Add two numbers
  subtract <a> <b>   Subtract b from a
  multiply <a> <b>   Multiply two numbers
  divide <a> <b>     Divide a by b
  power <a> <b>      Raise a to the power of b
  root <a> <b>       Take the b-th root of a
  history            Show calculations from this session
  clear              Remove all calculations from history
  undo               Undo the last change to history
  redo               Redo the last undone change
  save               Save history to CSV
  load               Load saved history from CSV
  help               Show this message
  exit               Quit the calculator
"""


class Calculator:
    """Facade over configuration, operations, history, and undo support."""

    def __init__(self, config: CalculatorConfig = None):
        """Wire together the subsystems the REPL depends on."""
        self.config = config or CalculatorConfig()
        self.history_manager = HistoryManager(self.config)
        self.caretaker = Caretaker()
        self.logger = LoggingObserver()
        self.history_manager.attach(self.logger)
        self.history_manager.attach(AutoSaveObserver(self.history_manager))

    @property
    def history(self) -> list:
        """Return the current list of calculations."""
        return self.history_manager.history

    def perform(self, name: str, a: float, b: float) -> Calculation:
        """Run an operation, record it, and return the calculation."""
        operation = OperationFactory.create(name)
        calculation = Calculation.create(operation, a, b)
        calculation.result = round(calculation.result, self.config.precision)
        self.caretaker.save(self.history_manager.history)
        self.history_manager.add(calculation)
        return calculation

    def undo(self) -> bool:
        """Restore the previous history. Return False if nothing to undo."""
        restored = self.caretaker.undo(self.history_manager.history)
        if restored is None:
            return False
        self.history_manager.history = restored
        return True

    def redo(self) -> bool:
        """Reapply an undone history. Return False if nothing to redo."""
        restored = self.caretaker.redo(self.history_manager.history)
        if restored is None:
            return False
        self.history_manager.history = restored
        return True

    def clear(self) -> None:
        """Empty the history, saving a snapshot first so it can be undone."""
        self.caretaker.save(self.history_manager.history)
        self.history_manager.clear()

    def save(self) -> None:
        """Persist the history to CSV."""
        self.history_manager.save()

    def load(self):
        """Return the saved history as a DataFrame."""
        return self.history_manager.load()


def calculator_repl(calculator: Calculator = None) -> None:
    """Run the interactive calculator REPL."""
    calculator = calculator or Calculator()
    print("Welcome to the advanced calculator! Type 'help' for commands.")

    while True:
        user_input = input(">>> ").strip()

        # LBYL: ignore empty input before trying to interpret it
        if not user_input:
            continue

        command = user_input.lower()

        if command == "exit":
            print("Exiting calculator...")
            break

        if command == "help":
            print(MENU)
            continue

        if command == "history":
            if not calculator.history:
                print("No calculations yet.")
            else:
                for entry in calculator.history:
                    print(entry)
            continue

        if command == "clear":
            calculator.clear()
            print("History cleared.")
            continue

        if command == "undo":
            print("Undone." if calculator.undo() else "Nothing to undo.")
            continue

        if command == "redo":
            print("Redone." if calculator.redo() else "Nothing to redo.")
            continue

        if command == "save":
            try:
                calculator.save()
                print("History saved.")
            except CalculatorError as error:
                print(error)
            continue

        if command == "load":
            try:
                frame = calculator.load()
                print("No saved history found." if frame.empty else frame.to_string(index=False))
            except CalculatorError as error:
                print(error)
            continue

        # EAFP: attempt the calculation and report any calculator error
        try:
            parts = user_input.split()
            a, b = validate_operands(parts[1:])
            calculation = calculator.perform(parts[0].lower(), a, b)
        except CalculatorError as error:
            print(error)
            continue

        print(f"Result: {calculation.result}")