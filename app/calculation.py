"""Calculation records produced by the calculator."""

from dataclasses import dataclass, field
from datetime import datetime

from app.operations import Operation


@dataclass
class Calculation:
    """A single completed calculation."""

    operation: Operation
    operand_a: float
    operand_b: float
    result: float
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, operation: Operation, a: float, b: float) -> "Calculation":
        """Execute the operation and return a Calculation record."""
        return cls(operation=operation, operand_a=a, operand_b=b, result=operation.execute(a, b))

    def to_dict(self) -> dict:
        """Return the calculation as a dictionary for pandas."""
        return {
            "operation": self.operation.name,
            "operand_a": self.operand_a,
            "operand_b": self.operand_b,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        """Return a readable record of the calculation."""
        return f"{self.operand_a} {self.operation.symbol} {self.operand_b} = {self.result}"