"""Tests for observers and the pandas-backed history manager."""

import pytest

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.history import AutoSaveObserver, HistoryManager, LoggingObserver
from app.operations import Addition, Multiplication


@pytest.fixture
def manager(tmp_path, monkeypatch):
    """Return a history manager writing to a temporary directory."""
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    return HistoryManager(CalculatorConfig(base_dir=tmp_path))


def make_calculation(a=2, b=3):
    """Return a simple addition calculation."""
    return Calculation.create(Addition(), a, b)


def test_add_appends_to_history(manager):
    """Adding a calculation stores it."""
    manager.add(make_calculation())
    assert len(manager.history) == 1


def test_history_is_trimmed_to_max_size(manager):
    """History never grows beyond the configured maximum."""
    manager.config.max_history_size = 2
    for index in range(5):
        manager.add(make_calculation(index, 1))
    assert len(manager.history) == 2


def test_clear_empties_history(manager):
    """Clearing removes every calculation."""
    manager.add(make_calculation())
    manager.clear()
    assert manager.history == []


def test_to_dataframe_is_empty_without_history(manager):
    """An empty history produces an empty DataFrame with the right columns."""
    frame = manager.to_dataframe()
    assert frame.empty
    assert list(frame.columns) == HistoryManager.COLUMNS


def test_to_dataframe_contains_rows(manager):
    """Each calculation becomes a row in the DataFrame."""
    manager.add(make_calculation())
    manager.add(Calculation.create(Multiplication(), 4, 5))
    frame = manager.to_dataframe()
    assert len(frame) == 2
    assert frame.iloc[1]["operation"] == "multiply"


def test_save_then_load_round_trips(manager):
    """History saved to CSV can be read back."""
    manager.add(make_calculation())
    manager.save()
    assert len(manager.load()) == 1


def test_load_without_a_file_returns_empty(manager):
    """Loading before anything is saved returns an empty DataFrame."""
    assert manager.load().empty


def test_save_failure_raises_operation_error(manager, monkeypatch):
    """A filesystem failure during save raises OperationError."""
    def fail(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr("pandas.DataFrame.to_csv", fail)
    manager.add(make_calculation())
    with pytest.raises(OperationError, match="Could not save history"):
        manager.save()


def test_load_failure_raises_operation_error(manager, monkeypatch):
    """A read failure during load raises OperationError."""
    manager.add(make_calculation())
    manager.save()
    def fail(*args, **kwargs):
        raise OSError("unreadable")
    monkeypatch.setattr("pandas.read_csv", fail)
    with pytest.raises(OperationError, match="Could not load history"):
        manager.load()


def test_logging_observer_records_calculations(manager):
    """The logging observer records each calculation it sees."""
    observer = LoggingObserver()
    manager.attach(observer)
    manager.add(make_calculation())
    assert observer.entries == ["2 + 3 = 5"]


def test_auto_save_observer_saves_when_enabled(manager):
    """The auto-save observer writes the file when auto-save is on."""
    manager.config.auto_save = True
    manager.attach(AutoSaveObserver(manager))
    manager.add(make_calculation())
    assert manager.config.history_file.exists()


def test_auto_save_observer_skips_when_disabled(manager):
    """The auto-save observer does nothing when auto-save is off."""
    manager.config.auto_save = False
    manager.attach(AutoSaveObserver(manager))
    manager.add(make_calculation())
    assert not manager.config.history_file.exists()