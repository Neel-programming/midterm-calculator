"""Tests for the operation strategies and factory."""

import pytest

from app.exceptions import OperationError
from app.operations import (
    Addition,
    Division,
    Multiplication,
    OperationFactory,
    Power,
    Root,
    Subtraction,
)


@pytest.mark.parametrize("operation_class, a, b, expected", [
    (Addition, 2, 3, 5),
    (Addition, -1, 1, 0),
    (Subtraction, 5, 3, 2),
    (Subtraction, 3, 5, -2),
    (Multiplication, 4, 5, 20),
    (Multiplication, -2, 3, -6),
    (Division, 10, 2, 5),
    (Division, -6, 3, -2),
    (Power, 2, 10, 1024),
    (Power, 5, 0, 1),
    (Root, 27, 3, 3),
    (Root, 16, 2, 4),
])
def test_execute(operation_class, a, b, expected):
    """Each strategy returns the correct result."""
    assert operation_class().execute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("operation_class, a, b, message", [
    (Division, 1, 0, "Division by zero"),
    (Root, 8, 0, "zeroth root"),
    (Root, -8, 3, "negative number"),
])
def test_execute_rejects_invalid_operands(operation_class, a, b, message):
    """Invalid operands raise OperationError."""
    with pytest.raises(OperationError, match=message):
        operation_class().execute(a, b)


@pytest.mark.parametrize("name, operation_class", [
    ("add", Addition),
    ("subtract", Subtraction),
    ("multiply", Multiplication),
    ("divide", Division),
    ("power", Power),
    ("root", Root),
])
def test_factory_creates_correct_strategy(name, operation_class):
    """The factory returns the right strategy for each name."""
    assert isinstance(OperationFactory.create(name), operation_class)


def test_factory_rejects_unknown_operation():
    """An unsupported name raises OperationError."""
    with pytest.raises(OperationError, match="Unknown operation 'nonsense'."):
        OperationFactory.create("nonsense")


def test_factory_lists_supported_operations():
    """The factory reports every operation it supports."""
    assert OperationFactory.supported() == [
        "add", "subtract", "multiply", "divide", "power", "root",
        "modulus", "int_divide", "percent", "abs_diff",
    ]


def test_operation_str_returns_name():
    """An operation prints as its name."""
    assert str(Addition()) == "add"