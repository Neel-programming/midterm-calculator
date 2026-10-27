"""Tests for the Logger class."""

import pytest

from app.logger import Logger


@pytest.fixture
def logger(tmp_path):
    """Return a logger writing into a temporary directory with a unique name."""
    return Logger(tmp_path, name=f"test-{tmp_path.name}")


def test_log_directory_is_created(tmp_path):
    """Creating a logger creates its log directory."""
    target = tmp_path / "nested" / "logs"
    Logger(target, name="test-create")
    assert target.exists()


@pytest.mark.parametrize("level, message", [
    ("info", "an informational message"),
    ("warning", "a warning message"),
    ("error", "an error message"),
])
def test_messages_are_written(logger, level, message):
    """Each logging level writes its message to the log file."""
    getattr(logger, level)(message)
    assert message in logger.log_path.read_text()


def test_level_name_is_recorded(logger):
    """The log line records the severity of the message."""
    logger.error("something failed")
    assert "ERROR" in logger.log_path.read_text()


def test_handler_is_not_duplicated(tmp_path):
    """Creating a logger twice with the same name does not duplicate handlers."""
    first = Logger(tmp_path, name="test-duplicate")
    second = Logger(tmp_path, name="test-duplicate")
    assert len(second.logger.handlers) == 1
    first.info("only once")
    assert first.log_path.read_text().count("only once") == 1