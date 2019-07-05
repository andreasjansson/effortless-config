import pytest
from .config import config


def test_with_context_manager():
    with config.override(FLOAT_SETTING=0.8, A_BOOLEAN=True):
        assert config.FLOAT_SETTING * config.SOME_INTEGER_SETTING == 8
        assert config.A_BOOLEAN is True


def test_with_manual_reset():
    config.override(FLOAT_SETTING=0.8, A_BOOLEAN=True)
    assert config.FLOAT_SETTING * config.SOME_INTEGER_SETTING == 8
    assert config.A_BOOLEAN is True
    config.reset_to_defaults()
