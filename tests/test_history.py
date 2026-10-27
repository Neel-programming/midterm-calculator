"""Tests for observers and the pandas-backed history manager."""

import pytest

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.history import AutoSaveObserver, HistoryManager, LoggingObserver
from app.logger import Logger
from app.operations import Addition, Multiplication


@pytest.fixture
def config(tmp_path, monkeypatch):
    """Return a configuration pointing at temporary directories."""
    monkeypatch.delenv("CALCULATOR_MAX_HISTORY_SIZE", raising=False)
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)
    return CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")


@pytest.fixture
def manager(config):
    """Return a history manager writing to a temporary directory."""
    return HistoryManager(config)


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
    """History saved to CSV is rebuilt as Calculation objects on load."""
    manager.add(make_calculation())
    manager.save()
    manager.history = []
    loaded = manager.load()
    assert len(loaded) == 1
    assert isinstance(loaded[0], Calculation)
    assert loaded[0].result == 5


def test_load_without_a_file_returns_empty(manager):
    """Loading before anything is saved returns an empty list."""
    assert manager.load() == []


def test_load_rejects_malformed_history(manager):
    """A CSV missing required columns raises OperationError."""
    manager.config.history_dir.mkdir(parents=True, exist_ok=True)
    manager.config.history_file.write_text("wrong,columns\n1,2\n")
    with pytest.raises(OperationError, match="malformed"):
        manager.load()


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


def test_logging_observer_writes_to_log(manager, config):
    """The logging observer records each calculation in the log file."""
    logger = Logger(config.log_dir, name="test-observer")
    manager.attach(LoggingObserver(logger))
    manager.add(make_calculation())
    assert "add(2, 3) = 5" in logger.log_path.read_text()


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