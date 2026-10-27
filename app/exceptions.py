"""Custom exceptions for the calculator application."""


class CalculatorError(Exception):
    """Base class for all calculator errors."""


class ValidationError(CalculatorError):
    """Raised when user input fails validation."""


class OperationError(CalculatorError):
    """Raised when an operation cannot be performed."""


class ConfigurationError(CalculatorError):
    """Raised when configuration values are invalid."""