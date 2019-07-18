import pytest

from effortless_config import Config, setting


def test_types():
    class config(Config):
        MY_INT = setting(10)
        MY_FLOAT = setting(10.0)
        MY_STR = setting('foo')
        MY_BOOL = setting(True)
        MY_LIST = setting([1, 2, 3])
        MY_DICT = setting({'a': 1, 'b': 2, 'c': 3})
        MY_SHORTHAND_INT = 20

    assert config.MY_INT == 10
    assert config.MY_FLOAT == 10.0
    assert config.MY_STR == 'foo'
    assert config.MY_BOOL is True
    assert config.MY_LIST == [1, 2, 3]
    assert config.MY_DICT == {'a': 1, 'b': 2, 'c': 3}
    assert config.MY_SHORTHAND_INT == 20


def test_bad_type():

    with pytest.raises(ValueError):

        class config(Config):
            MY_LIST = setting(1j)


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


def test_method():
    class config(Config):
        groups = ['foo', 'bar']

        MY_INT = setting(10, foo=10, bar=20)
        MY_FLOAT = setting(10.0, bar=20.0)
        MY_STR = setting('foo', foo='asdf')

        @classmethod
        def MY_BOOL(cls):
            return True

    assert config.MY_INT == 10
    assert config.MY_FLOAT == 10.0
    assert config.MY_STR == 'foo'
    assert config.MY_BOOL() is True

    assert 'MY_INT' in config._settings
    assert 'MY_BOOL' not in config._settings


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


def test_badly_cased_shorthand():
    with pytest.raises(ValueError):

        class config(Config):
            adsf = 123


def test_badly_cased_setting():
    with pytest.raises(ValueError):

        class config(Config):
            adsf = setting(123)


def test_undefined_groups():
    with pytest.raises(ValueError):

        class config(Config):
            groups = ['foo', 'bar']
            MY_INT = setting(10, baz=20)


def test_set_group():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')
        S4 = 0.5
        S5 = setting([1, 2, 3], foo=[4, 5, 6])
        S6 = setting({'a': 1, 'b': 2, 'c': 3}, bar={'d': 4, 'e': 5})

    assert config.S1 == 10
    assert config.S4 == 0.5

    config.set_group('foo')
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'b'
    assert config.S4 == 0.5
    assert config.S5 == [4, 5, 6]
    assert config.S6 == {'a': 1, 'b': 2, 'c': 3}

    config.set_group('bar')
    assert config.S1 == 10
    assert config.S2 is False
    assert config.S3 == 'c'
    assert config.S4 == 0.5
    assert config.S5 == [1, 2, 3]
    assert config.S6 == {'d': 4, 'e': 5}


def test_set_default_group():
    class config(Config):
        groups = ['a', 'b']
        FOO = setting(10, a=20, b=30)

    config.set_group('default')
    assert config.FOO == 10


def test_set_default_group_without_groups():
    class config(Config):
        FOO = 10

    config.set_group('default')
    assert config.FOO == 10


def test_set_bad_group():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')
        S4 = 0.5

    with pytest.raises(ValueError):
        config.set_group('baz')


def test_set_group_from_args():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--configuration', 'foo'])
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'b'


def test_set_default_group_from_args():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--configuration', 'default'])
    assert config.S1 == 10
    assert config.S2 is True
    assert config.S3 == 'a'


def test_set_option_from_args():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        SECOND_OPTION = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')

    config.parse_args(['--s1', '30', '--second-option', 'false'])
    assert config.S1 == 30
    assert config.SECOND_OPTION is False
    assert config.S3 == 'a'


def test_set_shorthand_option_from_args():
    class config(Config):
        S1 = 10
        S2 = True

    config.parse_args(['--s1', '30', '--s2', 'false'])
    assert config.S1 == 30
    assert config.S2 is False


def test_set_group_and_option_from_args():
    class config(Config):
        groups = ['foo', 'bar']

        S1 = setting(10, foo=20)
        S2 = setting(True, bar=False)
        S3 = setting('a', foo='b', bar='c')
        S4 = 0.5

    config.parse_args(['--s3', 'd', '--configuration', 'foo', '--s4', '1.5'])
    assert config.S1 == 20
    assert config.S2 is True
    assert config.S3 == 'd'
    assert config.S4 == 1.5


def test_set_list_from_args():
    class config(Config):
        S1 = [1, 2, 3]

    config.parse_args(['--s1', '[4, 5, 6]'])
    assert config.S1 == [4, 5, 6]


def test_bad_set_list_from_args():
    class config(Config):
        S1 = [1, 2, 3]

    with pytest.raises(SystemExit):
        config.parse_args(['--s1', '4,5,6'])


def test_set_dict_from_args():
    class config(Config):
        S1 = {'a': 1, 'b': 2}

    config.parse_args(['--s1', '{"c": 3, "d": 4}'])
    assert config.S1 == {'c': 3, 'd': 4}


def test_bad_set_dict_from_args():
    class config(Config):
        S1 = {'a': 1, 'b': 2}

    with pytest.raises(SystemExit):
        config.parse_args(['--s1', '{a: 1}'])


def test_set_bad_type_from_args():
    class config(Config):
        S1 = 10
        S2 = True

    with pytest.raises(SystemExit):
        config.parse_args(['--s1', 'foo'])


def test_repr():
    class c(Config):
        groups = ['a']
        A = setting(1, a=2)
        B = 2.0
        C = True
        D = 'foo'

    assert (
        repr(c)
        == """\
class c(Config):
    groups = ['a']
    A = 1
    B = 2.0
    C = True
    D = 'foo'"""
    )


def test_equal():
    class c(Config):
        groups = ['a']
        A = setting(1, a=2)
        B = 2.0
        C = True
        D = 'foo'

    class d(Config):
        B = 2.0
        A = 1
        D = 'foo'
        C = True

    assert c == d


def test_to_hash_string():
    class c(Config):
        groups = ['a']
        A = setting(1, a=2)
        B = 2.0
        C = True
        D = 'foo'

    class d(Config):
        B = 2.0
        A = 1
        D = 'foo'
        C = True

    assert c.to_hash_string() == d.to_hash_string()
    assert isinstance(c.to_hash_string(), str)
    assert len(c.to_hash_string()) > 3  # a reasonable assumption
