"""Validation helpers for user input."""

from app.exceptions import ValidationError


def validate_number(value: str, max_value: float = None) -> float:
    """Return value as a float, or raise ValidationError."""
    # EAFP: try the conversion rather than inspecting the string first
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"'{value}' is not a valid number.") from error

    # LBYL: check the magnitude only once we know we have a number
    if max_value is not None and abs(number) > max_value:
        raise ValidationError(f"Value {number} exceeds the maximum of {max_value}.")
    return number


def validate_operands(parts: list, max_value: float = None) -> tuple:
    """Return two validated operands from the parsed input parts."""
    # LBYL: check the shape of the input before converting anything
    if len(parts) != 2:
        raise ValidationError("Expected two numbers. Format: <operation> <a> <b>")
    return validate_number(parts[0], max_value), validate_number(parts[1], max_value)