"""Tests for the Calculator facade and the REPL."""

import pytest

from app.calculator_config import CalculatorConfig
from app.calculator import Calculator, calculator_repl


@pytest.fixture
def calculator(tmp_path, monkeypatch):
    """Return a calculator writing to a temporary directory."""
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    monkeypatch.delenv("CALCULATOR_PRECISION", raising=False)
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def run_repl(monkeypatch, capsys, typed, calculator=None):
    """Run the REPL with a scripted user and return everything printed."""
    notes = iter(typed + ["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(notes))
    calculator_repl(calculator)
    return capsys.readouterr().out


@pytest.mark.parametrize("name, a, b, expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 4, 5, 20),
    ("divide", 10, 2, 5),
    ("power", 2, 10, 1024),
    ("root", 27, 3, 3),
])
def test_perform_returns_result(calculator, name, a, b, expected):
    """The facade runs each operation and records it."""
    assert calculator.perform(name, a, b).result == pytest.approx(expected)
    assert len(calculator.history) == 1


def test_perform_rounds_to_configured_precision(calculator):
    """Results are rounded to the configured precision."""
    calculator.config.precision = 2
    assert calculator.perform("divide", 10, 3).result == 3.33


def test_undo_and_redo(calculator):
    """Undo removes the last calculation and redo restores it."""
    calculator.perform("add", 2, 3)
    assert calculator.undo() is True
    assert calculator.history == []
    assert calculator.redo() is True
    assert len(calculator.history) == 1


def test_undo_and_redo_return_false_when_empty(calculator):
    """Undo and redo report failure when there is nothing to do."""
    assert calculator.undo() is False
    assert calculator.redo() is False


def test_clear_can_be_undone(calculator):
    """Clearing history saves a snapshot so it can be restored."""
    calculator.perform("add", 2, 3)
    calculator.clear()
    assert calculator.history == []
    assert calculator.undo() is True
    assert len(calculator.history) == 1


def test_save_and_load(calculator):
    """The facade saves history and loads it back."""
    calculator.perform("add", 2, 3)
    calculator.save()
    assert len(calculator.load()) == 1


@pytest.mark.parametrize("typed, expected", [
    ("add 2 3", "Result: 5.0"),
    ("power 2 10", "Result: 1024.0"),
    ("root 27 3", "Result: 3.0"),
    ("divide 5 0", "Division by zero is not allowed."),
    ("root 8 0", "Cannot take the zeroth root."),
    ("modulus 5 3", "Unknown operation 'modulus'."),
    ("add two three", "is not a valid number"),
    ("add 1", "Expected two numbers"),
])
def test_repl_single_command(monkeypatch, capsys, calculator, typed, expected):
    """Each command produces the expected output."""
    assert expected in run_repl(monkeypatch, capsys, [typed], calculator)


def test_repl_help(monkeypatch, capsys, calculator):
    """Help prints the command menu."""
    assert "Available commands:" in run_repl(monkeypatch, capsys, ["help"], calculator)


def test_repl_history_when_empty(monkeypatch, capsys, calculator):
    """History reports when nothing has been calculated."""
    assert "No calculations yet." in run_repl(monkeypatch, capsys, ["history"], calculator)


def test_repl_history_lists_calculations(monkeypatch, capsys, calculator):
    """History lists each calculation performed."""
    output = run_repl(monkeypatch, capsys, ["add 2 3", "multiply 4 5", "history"], calculator)
    assert "2.0 + 3.0 = 5.0" in output
    assert "4.0 * 5.0 = 20.0" in output


def test_repl_clear(monkeypatch, capsys, calculator):
    """Clear empties the history."""
    output = run_repl(monkeypatch, capsys, ["add 2 3", "clear", "history"], calculator)
    assert "History cleared." in output
    assert "No calculations yet." in output


def test_repl_undo_and_redo(monkeypatch, capsys, calculator):
    """Undo and redo report what they did."""
    output = run_repl(monkeypatch, capsys, ["add 2 3", "undo", "redo"], calculator)
    assert "Undone." in output
    assert "Redone." in output


def test_repl_undo_and_redo_when_empty(monkeypatch, capsys, calculator):
    """Undo and redo report when there is nothing to do."""
    output = run_repl(monkeypatch, capsys, ["undo", "redo"], calculator)
    assert "Nothing to undo." in output
    assert "Nothing to redo." in output


def test_repl_save(monkeypatch, capsys, calculator):
    """Save confirms the history was written."""
    assert "History saved." in run_repl(monkeypatch, capsys, ["add 2 3", "save"], calculator)


def test_repl_load_without_saved_history(monkeypatch, capsys, calculator):
    """Load reports when there is no saved history."""
    calculator.config.auto_save = False
    assert "No saved history found." in run_repl(monkeypatch, capsys, ["load"], calculator)


def test_repl_load_shows_saved_history(monkeypatch, capsys, calculator):
    """Load prints the saved history."""
    output = run_repl(monkeypatch, capsys, ["add 2 3", "save", "load"], calculator)
    assert "add" in output


def test_repl_save_reports_errors(monkeypatch, capsys, calculator):
    """A save failure is reported rather than crashing."""
    calculator.config.auto_save = False
    def fail(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr("pandas.DataFrame.to_csv", fail)
    assert "Could not save history" in run_repl(monkeypatch, capsys, ["save"], calculator)


def test_repl_load_reports_errors(monkeypatch, capsys, calculator):
    """A load failure is reported rather than crashing."""
    calculator.perform("add", 2, 3)
    calculator.save()
    def fail(*args, **kwargs):
        raise OSError("unreadable")
    monkeypatch.setattr("pandas.read_csv", fail)
    assert "Could not load history" in run_repl(monkeypatch, capsys, ["load"], calculator)


def test_repl_ignores_blank_input(monkeypatch, capsys, calculator):
    """Pressing enter with no input re-prompts without an error."""
    output = run_repl(monkeypatch, capsys, ["", "add 1 1"], calculator)
    assert "Result: 2.0" in output


def test_repl_exit_message(monkeypatch, capsys, calculator):
    """Exiting prints a goodbye message."""
    assert "Exiting calculator..." in run_repl(monkeypatch, capsys, [], calculator)


def test_repl_creates_its_own_calculator(monkeypatch, capsys, tmp_path):
    """The REPL builds a default calculator when none is supplied."""
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    assert "Welcome" in run_repl(monkeypatch, capsys, [])