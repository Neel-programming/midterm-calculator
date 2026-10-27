"""Tests for configuration loading and validation."""

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove calculator settings so each test starts from defaults."""
    for name in [
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
        "CALCULATOR_AUTO_SAVE",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_defaults_are_applied(tmp_path):
    """Missing environment variables fall back to defaults."""
    config = CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")
    assert config.max_history_size == 100
    assert config.precision == 10
    assert config.max_input_value == 1e12
    assert config.default_encoding == "utf-8"
    assert config.auto_save is True


@pytest.mark.parametrize("value, expected", [
    ("true", True),
    ("TRUE", True),
    ("false", False),
    ("anything-else", False),
])
def test_auto_save_parsing(monkeypatch, tmp_path, value, expected):
    """Auto-save is true only for the string 'true', case-insensitively."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    config = CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")
    assert config.auto_save is expected


@pytest.mark.parametrize("name", ["CALCULATOR_MAX_HISTORY_SIZE", "CALCULATOR_PRECISION"])
def test_non_integer_setting_raises(monkeypatch, tmp_path, name):
    """A non-numeric integer setting raises ConfigurationError."""
    monkeypatch.setenv(name, "not-a-number")
    with pytest.raises(ConfigurationError, match="must be an integer"):
        CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")


def test_non_numeric_max_input_raises(monkeypatch, tmp_path):
    """A non-numeric max input value raises ConfigurationError."""
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "not-a-number")
    with pytest.raises(ConfigurationError, match="must be a number"):
        CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")


@pytest.mark.parametrize("name, value, message", [
    ("CALCULATOR_MAX_HISTORY_SIZE", "0", "Max history size must be positive"),
    ("CALCULATOR_MAX_HISTORY_SIZE", "-5", "Max history size must be positive"),
    ("CALCULATOR_PRECISION", "-1", "Precision cannot be negative"),
    ("CALCULATOR_MAX_INPUT_VALUE", "0", "Max input value must be positive"),
    ("CALCULATOR_MAX_INPUT_VALUE", "-10", "Max input value must be positive"),
])
def test_out_of_range_setting_raises(monkeypatch, tmp_path, name, value, message):
    """Settings outside the allowed range raise ConfigurationError."""
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigurationError, match=message):
        CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")


def test_paths_are_built_from_directories(monkeypatch, tmp_path):
    """Log and history file paths sit inside their configured directories."""
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "app.log")
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "saved.csv")
    config = CalculatorConfig(log_dir=tmp_path / "logs", history_dir=tmp_path / "history")
    assert config.log_file == tmp_path / "logs" / "app.log"
    assert config.history_file == tmp_path / "history" / "saved.csv"