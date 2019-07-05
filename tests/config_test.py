import pytest

from effortless_config import Config, setting


def test_types():
    class config(Config):
        MY_INT = setting(10)
        MY_FLOAT = setting(10.0)
        MY_STR = setting('foo')
        MY_BOOL = setting(True)

    assert config.MY_INT == 10
    assert config.MY_FLOAT == 10.0
    assert config.MY_STR == 'foo'
    assert config.MY_BOOL is True


def test_bad_type():

    with pytest.raises(ValueError):

        class config(Config):
            MY_LIST = setting([1, 2, 3])


def test_group_types():
    class config(Config):
        groups = ['foo', 'bar']

        MY_INT = setting(10, foo=10, bar=20)
        MY_FLOAT = setting(10.0, bar=20.0)
        MY_STR = setting('foo', foo='asdf')
        MY_BOOL = setting(True, bar=False)

    assert config.MY_INT == 10
    assert config.MY_FLOAT == 10.0
    assert config.MY_STR == 'foo'
    assert config.MY_BOOL is True


def test_none():
    class config(Config):
        FOO = setting(None)

    assert config.FOO is None
    assert config._settings['FOO'].type == str


def test_none_with_groups():
    class config(Config):
        groups = ['hello']
        FOO = setting(None, hello=123)

    assert config.FOO is None
    assert config._settings['FOO'].type == int


def test_undefined_groups():

    with pytest.raises(ValueError):

        class config(Config):
            groups = ['foo', 'bar']

            MY_INT = setting(10, baz=20)


class test_set_group:
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    assert config.S1 == 10

    config.set_group('foo')
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'b'

    config.set_group('bar')
    assert config.S1 == 10
    assert config.S2 is False
    assert config.S3 == 'c'


class test_set_group_from_args:
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--configuration', 'foo'])
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'b'


class test_set_option_from_args:
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        SECOND_OPTION = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--s1', '30', '--second-option', 'false'])
    assert config.S1 == 30
    assert config.SECOND_OPTION is False
    assert config.S3 == 'a'


class test_set_group_and_option_from_args:
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--s3', 'd', '--configuration', 'foo'])
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'd'
