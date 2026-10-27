"""Tests for configuration loading and validation."""

from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_defaults_are_applied(monkeypatch):
    """Missing environment variables fall back to defaults."""
    for name in [
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_AUTO_SAVE",
    ]:
        monkeypatch.delenv(name, raising=False)
    config = CalculatorConfig(base_dir=Path("./data"))
    assert config.max_history_size == 100
    assert config.precision == 10
    assert config.auto_save is True


@pytest.mark.parametrize("value, expected", [
    ("true", True),
    ("TRUE", True),
    ("false", False),
    ("anything-else", False),
])
def test_auto_save_parsing(monkeypatch, value, expected):
    """Auto-save is true only for the string 'true', case-insensitively."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    assert CalculatorConfig(base_dir=Path("./data")).auto_save is expected


@pytest.mark.parametrize("name", ["CALCULATOR_MAX_HISTORY_SIZE", "CALCULATOR_PRECISION"])
def test_non_integer_setting_raises(monkeypatch, name):
    """A non-numeric integer setting raises ConfigurationError."""
    monkeypatch.setenv(name, "not-a-number")
    with pytest.raises(ConfigurationError, match="must be an integer"):
        CalculatorConfig(base_dir=Path("./data"))


@pytest.mark.parametrize("name, value, message", [
    ("CALCULATOR_MAX_HISTORY_SIZE", "0", "Max history size must be positive"),
    ("CALCULATOR_MAX_HISTORY_SIZE", "-5", "Max history size must be positive"),
    ("CALCULATOR_PRECISION", "-1", "Precision cannot be negative"),
])
def test_out_of_range_setting_raises(monkeypatch, name, value, message):
    """Settings outside the allowed range raise ConfigurationError."""
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigurationError, match=message):
        CalculatorConfig(base_dir=Path("./data"))


def test_history_file_sits_inside_base_dir(tmp_path, monkeypatch):
    """The history file path is built from the base directory."""
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "my_history.csv")
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.history_file == tmp_path / "my_history.csv"