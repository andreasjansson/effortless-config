# Effortless Config

[![PyPI version](https://badge.fury.io/py/effortless-config.svg)](https://badge.fury.io/py/effortless-config) [![CircleCI](https://circleci.com/gh/andreasjansson/effortless-config/tree/master.svg?style=svg)](https://circleci.com/gh/andreasjansson/effortless-config/tree/master)

_Globally scoped configuration with argparse integration._

## Installation

```
pip install effortless-config
```

## Rationale

1. When building machine learning models, I often find myself with a file named `config.py` that has a bunch of global variables that I reference throughout the codebase.
2. As the work progresses, I end up with _groups_ of specific configuration settings that correspond to specific experiments.
3. I want to be able to select configuration group on the command line when I start an experiment.
4. And I want to be able to override certain settings within that experiment, from the command line.

## Usage

### Defining configuration

Inside some file in your project, for example `example/config.py`:

```python
from effortless_config import Config, setting

class config(Config):  # notice lowercase c

    groups = ['experiment1', 'experiment2']

    SOME_INTEGER_SETTING = setting(10, experiment1=20, experiment2=30)
    FLOAT_SETTING = setting(0.5)
    A_BOOLEAN = setting(False, experiment1=True)
    MY_STRING_SETTING = setting('foo', experiment2='bar')
    SOME_OTHER_INTEGER = 100
```

First we create a class that extends `effortless_config.Config`. Inside it we add configurable parameters with the `effortless_config.setting` method. `setting` has the signature:

```python
def setting(default: T, **kwargs: T) -> T
```

...where `T` is `Union[int, float, str, bool, NoneType]` and `kwargs` is a map from group names to values.


In this example, `FLOAT_SETTING` has no groups defined, so this setting will use the default value for all groups. It can still be overridden on the command line though. But `SOME_OTHER_INTEGER` will always be fixed, since it's not wrapped in `setting`.

### Using the configuration

Then in your code you can use these settings, for example in`example/main.py`:

```python
from .config import config

if __name__ == '__main__':
    config.parse_args()
    print(f'SOME_INTEGER_SETTING is {config.SOME_INTEGER_SETTING}')
    print(f'FLOAT_SETTING is {config.FLOAT_SETTING}')
    print(f'A_BOOLEAN is {config.A_BOOLEAN}')
    print(f'MY_STRING_SETTING is {config.MY_STRING_SETTING}')
    print(f'SOME_OTHER_INTEGER is {config.SOME_OTHER_INTEGER}')
```

When we invoke main.py without any arguments, we get the default settings:

```console
$ python -m example.main
SOME_INTEGER_SETTING is 10
FLOAT_SETTING is 0.5
A_BOOLEAN is False
MY_STRING_SETTING is foo
SOME_OTHER_INTEGER is 100
```

When we pass an configuration group using the `--configuration` parameter, we get different values:

```console
$ python -m example.main --configuration experiment1
SOME_INTEGER_SETTING is 20
FLOAT_SETTING is 0.5
A_BOOLEAN is True
MY_STRING_SETTING is foo
SOME_OTHER_INTEGER is 100
```

We can also override individual settings:

```console
$ python -m example.main --some-integer-setting 40 --float-setting -5
SOME_INTEGER_SETTING is 40
FLOAT_SETTING is -5.0
A_BOOLEAN is False
MY_STRING_SETTING is foo
SOME_OTHER_INTEGER is 100
```

As well as combining groups with individual settings:

```console
$ python -m example.main --configuration experiment1 --some-integer-setting 40
SOME_INTEGER_SETTING is 40
FLOAT_SETTING is 0.5
A_BOOLEAN is True
MY_STRING_SETTING is foo
SOME_OTHER_INTEGER is 100
```

You can see all available settings using the `-h` flag:

```console
$ python -m example.main -h
usage: main.py [-h] [--configuration {experiment1,experiment2}]
               [--some-integer-setting SOME_INTEGER_SETTING]
               [--float-setting FLOAT_SETTING] [--a-boolean {true,false}]
               [--my-string-setting MY_STRING_SETTING]

optional arguments:
  -h, --help            show this help message and exit
  --configuration {experiment1,experiment2}, -c {experiment1,experiment2}
  --some-integer-setting SOME_INTEGER_SETTING
  --float-setting FLOAT_SETTING
  --a-boolean {true,false}
  --my-string-setting MY_STRING_SETTING
```

## Testing

When writing tests, you can use the `config.override` context manager to override individual settings:

```python
import pytest
from .config import config

def test_with_context_manager():
    with config.override(FLOAT_SETTING=0.8, A_BOOLEAN=True):
        assert config.FLOAT_SETTING * config.SOME_INTEGER_SETTING == 8
        assert config.A_BOOLEAN is True
```

The `config.override` method can also be used without context management in conjunction with `config.reset_to_defaults`:

```python
def test_with_manual_reset():
    config.override(FLOAT_SETTING=0.8, A_BOOLEAN=True)
    assert config.FLOAT_SETTING * config.SOME_INTEGER_SETTING == 8
    assert config.A_BOOLEAN is True
    config.reset_to_defaults()
```
