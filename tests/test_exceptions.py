"""Tests for the custom exception hierarchy."""

import pytest

from app.exceptions import (
    CalculatorError,
    ConfigurationError,
    OperationError,
    ValidationError,
)


@pytest.mark.parametrize("error_class", [
    ValidationError,
    OperationError,
    ConfigurationError,
])
def test_errors_inherit_from_calculator_error(error_class):
    """Every custom error is a CalculatorError."""
    assert issubclass(error_class, CalculatorError)


@pytest.mark.parametrize("error_class, message", [
    (ValidationError, "bad input"),
    (OperationError, "bad operation"),
    (ConfigurationError, "bad config"),
])
def test_errors_carry_their_message(error_class, message):
    """Each error preserves the message it was raised with."""
    with pytest.raises(error_class, match=message):
        raise error_class(message)