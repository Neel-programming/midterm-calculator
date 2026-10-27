"""Operation classes implementing the Strategy pattern."""

from abc import ABC, abstractmethod

from app.exceptions import OperationError


class Operation(ABC):
    """Strategy interface for a single arithmetic operation."""

    name = "operation"
    symbol = "?"

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Return the result of applying this operation."""

    def __str__(self) -> str:
        """Return the operation name."""
        return self.name


class Addition(Operation):
    """Add two numbers."""

    name = "add"
    symbol = "+"

    def execute(self, a: float, b: float) -> float:
        """Return a plus b."""
        return a + b


class Subtraction(Operation):
    """Subtract one number from another."""

    name = "subtract"
    symbol = "-"

    def execute(self, a: float, b: float) -> float:
        """Return a minus b."""
        return a - b


class Multiplication(Operation):
    """Multiply two numbers."""

    name = "multiply"
    symbol = "*"

    def execute(self, a: float, b: float) -> float:
        """Return a times b."""
        return a * b


class Division(Operation):
    """Divide one number by another."""

    name = "divide"
    symbol = "/"

    def execute(self, a: float, b: float) -> float:
        """Return a divided by b."""
        # LBYL: check the divisor before attempting the division
        if b == 0:
            raise OperationError("Division by zero is not allowed.")
        return a / b


class Power(Operation):
    """Raise one number to the power of another."""

    name = "power"
    symbol = "^"

    def execute(self, a: float, b: float) -> float:
        """Return a raised to the power of b."""
        return a ** b


class Root(Operation):
    """Take the b-th root of a."""

    name = "root"
    symbol = "root"

    def execute(self, a: float, b: float) -> float:
        """Return the b-th root of a."""
        # LBYL: reject inputs that have no real root before computing
        if b == 0:
            raise OperationError("Cannot take the zeroth root.")
        if a < 0:
            raise OperationError("Cannot take the root of a negative number.")
        return a ** (1 / b)


class OperationFactory:
    """Factory that creates Operation strategies by name."""

    _operations = {
        "add": Addition,
        "subtract": Subtraction,
        "multiply": Multiplication,
        "divide": Division,
        "power": Power,
        "root": Root,
    }

    @classmethod
    def create(cls, name: str) -> Operation:
        """Return an Operation instance for the given name."""
        # LBYL: confirm the operation exists before creating it
        if name not in cls._operations:
            raise OperationError(f"Unknown operation '{name}'.")
        return cls._operations[name]()

    @classmethod
    def supported(cls) -> list:
        """Return the list of supported operation names."""
        return list(cls._operations)