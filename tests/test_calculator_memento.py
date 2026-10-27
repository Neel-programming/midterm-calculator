"""Tests for the memento and caretaker."""

from app.calculator_memento import CalculatorMemento, Caretaker


def test_memento_restores_a_copy():
    """Restoring returns a copy, not the original list."""
    original = ["a", "b"]
    memento = CalculatorMemento(original)
    restored = memento.restore()
    assert restored == original
    assert restored is not original


def test_memento_has_a_timestamp():
    """Every memento records when it was created."""
    assert CalculatorMemento([]).timestamp is not None


def test_undo_returns_none_when_empty():
    """Undo with nothing saved returns None."""
    assert Caretaker().undo(["current"]) is None


def test_redo_returns_none_when_empty():
    """Redo with nothing undone returns None."""
    assert Caretaker().redo(["current"]) is None


def test_undo_restores_previous_state():
    """Undo returns the state that was saved."""
    caretaker = Caretaker()
    caretaker.save(["one"])
    assert caretaker.undo(["one", "two"]) == ["one"]


def test_redo_reapplies_undone_state():
    """Redo returns the state that undo moved away from."""
    caretaker = Caretaker()
    caretaker.save(["one"])
    caretaker.undo(["one", "two"])
    assert caretaker.redo(["one"]) == ["one", "two"]


def test_save_clears_the_redo_stack():
    """A new save discards any redo history."""
    caretaker = Caretaker()
    caretaker.save(["one"])
    caretaker.undo(["one", "two"])
    caretaker.save(["three"])
    assert caretaker.redo(["three"]) is None


def test_clear_empties_both_stacks():
    """Clearing removes undo and redo history."""
    caretaker = Caretaker()
    caretaker.save(["one"])
    caretaker.undo(["one", "two"])
    caretaker.clear()
    assert caretaker.undo(["x"]) is None
    assert caretaker.redo(["x"]) is None