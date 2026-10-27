"""Tests for the Calculation record."""

import pytest

from app.calculation import Calculation
from app.operations import Addition, Division, OperationFactory


@pytest.mark.parametrize("name, a, b, expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 4, 5, 20),
    ("divide", 10, 2, 5),
    ("power", 2, 8, 256),
    ("root", 81, 4, 3),
])
def test_create_computes_result(name, a, b, expected):
    """Creating a calculation runs the operation."""
    calculation = Calculation.create(OperationFactory.create(name), a, b)
    assert calculation.result == pytest.approx(expected)


def test_create_stores_operands():
    """A calculation remembers the operands it was created with."""
    calculation = Calculation.create(Addition(), 2, 3)
    assert calculation.operand_a == 2
    assert calculation.operand_b == 3


def test_to_dict_contains_every_column():
    """The dictionary form carries all fields needed by pandas."""
    result = Calculation.create(Addition(), 2, 3).to_dict()
    assert set(result) == {"operation", "operand_a", "operand_b", "result", "timestamp"}
    assert result["operation"] == "add"


@pytest.mark.parametrize("name, a, b, expected", [
    ("add", 2, 3, "2 + 3 = 5"),
    ("divide", 10, 2, "10 / 2 = 5.0"),
    ("power", 2, 3, "2 ^ 3 = 8"),
])
def test_str_is_readable(name, a, b, expected):
    """A calculation prints a readable record of itself."""
    assert str(Calculation.create(OperationFactory.create(name), a, b)) == expected


def test_create_propagates_operation_errors():
    """An invalid operation raises rather than producing a record."""
    with pytest.raises(Exception):
        Calculation.create(Division(), 1, 0)


def test_timestamp_is_set():
    """Every calculation records when it happened."""
    assert Calculation.create(Addition(), 1, 1).timestamp is not None