"""Validation helpers for user input."""

from app.exceptions import ValidationError


def validate_number(value: str) -> float:
    """Return value as a float, or raise ValidationError."""
    # EAFP: try the conversion rather than checking the string first
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"'{value}' is not a valid number.") from error


def validate_operands(parts: list) -> tuple:
    """Return two validated operands from the parsed input parts."""
    # LBYL: check the shape of the input before converting anything
    if len(parts) != 2:
        raise ValidationError("Expected two numbers. Format: <operation> <a> <b>")
    return validate_number(parts[0]), validate_number(parts[1])