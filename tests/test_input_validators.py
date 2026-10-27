"""Tests for the input validators."""

import pytest

from app.exceptions import ValidationError
from app.input_validators import validate_number, validate_operands


@pytest.mark.parametrize("value, expected", [
    ("5", 5.0),
    ("-3.5", -3.5),
    ("0", 0.0),
    ("1e3", 1000.0),
])
def test_validate_number_accepts_valid_input(value, expected):
    """Numeric strings convert to floats."""
    assert validate_number(value) == expected


@pytest.mark.parametrize("value", ["abc", "", None, "2 3"])
def test_validate_number_rejects_invalid_input(value):
    """Non-numeric values raise ValidationError."""
    with pytest.raises(ValidationError):
        validate_number(value)


def test_validate_operands_returns_two_floats():
    """A well-formed pair converts to two floats."""
    assert validate_operands(["2", "3"]) == (2.0, 3.0)


@pytest.mark.parametrize("parts", [[], ["2"], ["2", "3", "4"]])
def test_validate_operands_rejects_wrong_count(parts):
    """Anything other than two operands raises ValidationError."""
    with pytest.raises(ValidationError, match="Expected two numbers"):
        validate_operands(parts)