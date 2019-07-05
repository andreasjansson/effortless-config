import pytest
from effortless_config import Config, setting


class config(Config):
    FOO = setting(10)


def teardown_function():
    config.reset_to_defaults()


def test_global_override():
    config.override(FOO=100)
    assert config.FOO == 100

    config.reset_to_defaults()
    assert config.FOO == 10


def test_multiple_global_overrides():
    config.override(FOO=100)
    assert config.FOO == 100

    config.override(FOO=1000)
    assert config.FOO == 1000

    config.reset_to_defaults()
    assert config.FOO == 10


def test_local_override():
    with config.override(FOO=100):
        assert config.FOO == 100

    assert config.FOO == 10


def test_nested_local_override():
    with config.override(FOO=100):
        assert config.FOO == 100
        with config.override(FOO=1000):
            assert config.FOO == 1000

    assert config.FOO == 10


def test_local_and_global_override():
    config.override(FOO=100)
    assert config.FOO == 100

    with config.override(FOO=1000):
        assert config.FOO == 1000

    assert config.FOO == 100

    config.reset_to_defaults()
    assert config.FOO == 10
