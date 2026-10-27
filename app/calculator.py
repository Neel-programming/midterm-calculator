"""Facade and REPL interface for the calculator application."""

from colorama import Fore, Style, init

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import Caretaker
from app.exceptions import CalculatorError
from app.history import AutoSaveObserver, HistoryManager, LoggingObserver
from app.input_validators import validate_operands
from app.logger import Logger
from app.operations import OperationFactory

init(autoreset=True)

COMMAND_HELP = {
    "history": "Display calculation history",
    "clear": "Clear calculation history",
    "undo": "Undo the last calculation",
    "redo": "Redo the last undone calculation",
    "save": "Save calculation history to file",
    "load": "Load calculation history from file",
    "help": "Display this message",
    "exit": "Exit the application",
}


def build_menu() -> str:
    """Build the help menu from the registered operations and commands."""
    lines = [f"{Fore.CYAN}Available commands:{Style.RESET_ALL}"]
    for name in OperationFactory.supported():
        operation = OperationFactory.create(name)
        lines.append(f"  {Fore.GREEN}{name:<12}{Style.RESET_ALL} <a> <b>   "
                     f"Apply {operation.symbol}")
    for name, description in COMMAND_HELP.items():
        lines.append(f"  {Fore.GREEN}{name:<12}{Style.RESET_ALL}           {description}")
    return "\n".join(lines)


class Calculator:
    """Facade over configuration, operations, history, logging, and undo support."""

    def __init__(self, config: CalculatorConfig = None):
        """Wire together the subsystems the REPL depends on."""
        self.config = config or CalculatorConfig()
        self.logger = Logger(
            self.config.log_dir,
            self.config.log_file.name,
            self.config.default_encoding,
        )
        self.history_manager = HistoryManager(self.config, self.logger)
        self.caretaker = Caretaker()
        self.history_manager.attach(LoggingObserver(self.logger))
        self.history_manager.attach(AutoSaveObserver(self.history_manager))
        self.logger.info("Calculator started.")

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
        self.logger.info("Undo performed.")
        return True

    def redo(self) -> bool:
        """Reapply an undone history. Return False if nothing to redo."""
        restored = self.caretaker.redo(self.history_manager.history)
        if restored is None:
            return False
        self.history_manager.history = restored
        self.logger.info("Redo performed.")
        return True

    def clear(self) -> None:
        """Empty the history, saving a snapshot first so it can be undone."""
        self.caretaker.save(self.history_manager.history)
        self.history_manager.clear()
        self.logger.info("History cleared.")

    def save(self) -> None:
        """Persist the history to CSV."""
        self.history_manager.save()
        self.logger.info("History saved.")

    def load(self) -> list:
        """Load the saved history from CSV."""
        loaded = self.history_manager.load()
        self.logger.info(f"History loaded with {len(loaded)} entries.")
        return loaded


def calculator_repl(calculator: Calculator = None) -> None:
    """Run the interactive calculator REPL."""
    calculator = calculator or Calculator()
    print(f"{Fore.CYAN}Welcome to the advanced calculator! "
          f"Type 'help' for commands.{Style.RESET_ALL}")

    while True:
        user_input = input(f"{Fore.YELLOW}>>> {Style.RESET_ALL}").strip()

        # LBYL: ignore empty input before trying to interpret it
        if not user_input:
            continue

        command = user_input.lower()

        if command == "exit":
            print(f"{Fore.CYAN}Exiting calculator...{Style.RESET_ALL}")
            calculator.logger.info("Calculator exited.")
            break

        if command == "help":
            print(build_menu())
            continue

        if command == "history":
            if not calculator.history:
                print(f"{Fore.YELLOW}No calculations yet.{Style.RESET_ALL}")
            else:
                for entry in calculator.history:
                    print(entry)
            continue

        if command == "clear":
            calculator.clear()
            print(f"{Fore.GREEN}History cleared.{Style.RESET_ALL}")
            continue

        if command == "undo":
            message = "Undone." if calculator.undo() else "Nothing to undo."
            print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
            continue

        if command == "redo":
            message = "Redone." if calculator.redo() else "Nothing to redo."
            print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
            continue

        if command == "save":
            try:
                calculator.save()
                print(f"{Fore.GREEN}History saved.{Style.RESET_ALL}")
            except CalculatorError as error:
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            continue

        if command == "load":
            try:
                loaded = calculator.load()
                if not loaded:
                    print(f"{Fore.YELLOW}No saved history found.{Style.RESET_ALL}")
                else:
                    for entry in loaded:
                        print(entry)
            except CalculatorError as error:
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            continue

        # EAFP: attempt the calculation and report any calculator error
        try:
            parts = user_input.split()
            a, b = validate_operands(parts[1:], calculator.config.max_input_value)
            calculation = calculator.perform(parts[0].lower(), a, b)
        except CalculatorError as error:
            calculator.logger.error(str(error))
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            continue

        print(f"{Fore.GREEN}Result: {calculation.result}{Style.RESET_ALL}")