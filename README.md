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

## Basic usage

First, define a class that extends `effortless_config.Config` and specify your default configuration values inside it:

```python
from effortless_config import Config

class config(Config):  # lowercase "c" optional

    SOME_INTEGER_SETTING = 10
    FLOAT_SETTING = 0.5
    A_BOOLEAN = False
    MY_STRING_SETTING = 'foo'
```

Then you can refer to these settings elsewhere in your code base:

```python
def main():
    print(f'SOME_INTEGER_SETTING is {config.SOME_INTEGER_SETTING}')
    print(f'FLOAT_SETTING is {config.FLOAT_SETTING}')
    print(f'A_BOOLEAN is {config.A_BOOLEAN}')
    print(f'MY_STRING_SETTING is {config.MY_STRING_SETTING}')
```

The function `config.parse_args()` creates an [argparse](https://docs.python.org/3/library/argparse.html) parser from your configuration. If we put the two previous code snippets in a file called `basic_example.py` and finish it off with

```python
if __name__ == '__main__':
    config.parse_args()
    main()
```

...we can see the available settings with `-h/--help`:

```console
$ python basic_example.py --help
usage: basic_example.py [-h] [--some-integer-setting SOME_INTEGER_SETTING]
                        [--float-setting FLOAT_SETTING] [--a-boolean {true,false}]
                        [--my-string-setting MY_STRING_SETTING]

optional arguments:
  -h, --help            show this help message and exit
  --some-integer-setting SOME_INTEGER_SETTING
  --float-setting FLOAT_SETTING
  --a-boolean {true,false}
  --my-string-setting MY_STRING_SETTING
```

We can then override configuration settings from the command line:

```console
$ python basic_example.py
SOME_INTEGER_SETTING is 10
FLOAT_SETTING is 0.5
A_BOOLEAN is False
MY_STRING_SETTING is foo

$ python basic_example.py --some-integer-setting 1000
SOME_INTEGER_SETTING is 1000
FLOAT_SETTING is 0.5
A_BOOLEAN is False
MY_STRING_SETTING is foo
```

## Using _groups_

Configuration _groups_ are families of settings that you want to tie together. For example, you might have some machine learning problem for which you have a large model and a small model, and you want to easily switch between the two models without having to specify all parameters on the command line every time.

To specify groups, use the `settings(...)` function:

```python
from effortless_config import Config, setting

class config(Config):
    groups = ['large', 'small']

    NUM_LAYERS = setting(default=5, large=10, small=3)
    NUM_UNITS = setting(default=128, large=512, small=32)
    USE_SKIP_CONNECTIONS = setting(default=True, small=False)
    LEARNING_RATE = 0.1
    OPTIMIZER = 'adam'
```

`setting(...)` has the signature:

```python
def setting(default: T, **kwargs: T) -> T
```

...where `T` is `Union[int, float, str, bool, NoneType]` and `kwargs` is a map from group names to values. Specifying parameters by value is shorthand for a `setting` with no groups, i.e. `SOME_KEY = 'value'` is equivalent to `SOME_KEY = setting(default='value')`.

When using groups you must first define the group names using the `config.groups` list.

Then in your code you can use these settings like in the basic example

```python
def main():
    print(f'NUM_LAYERS is {config.NUM_LAYERS}')
    print(f'NUM_UNITS is {config.NUM_UNITS}')
    print(f'USE_SKIP_CONNECTIONS is {config.USE_SKIP_CONNECTIONS}')
    print(f'LEARNING_RATE is {config.LEARNING_RATE}')
    print(f'OPTIMIZER is {config.OPTIMIZER}')


if __name__ == '__main__':
    config.parse_args()
    main()
```

Now we see an additional `--configuration` option when we ask for `--help`:

```console
$ python group_example.py --help
usage: group_example.py [-h] [--configuration {default,large,small}]
                        [--num-layers NUM_LAYERS] [--num-units NUM_UNITS]
                        [--use-skip-connections {true,false}]
                        [--learning-rate LEARNING_RATE] [--optimizer OPTIMIZER]

optional arguments:
  -h, --help            show this help message and exit
  --configuration {default,large,small}, -c {default,large,small}
  --num-layers NUM_LAYERS
  --num-units NUM_UNITS
  --use-skip-connections {true,false}
  --learning-rate LEARNING_RATE
  --optimizer OPTIMIZER
```

The `--configuration` option specifies the configuration group, and defaults to `default` if omitted.

For example:

```console
$ python group_example.py
NUM_LAYERS is 5
NUM_UNITS is 128
USE_SKIP_CONNECTIONS is True
LEARNING_RATE is 0.1
OPTIMIZER is adam

$ python group_example.py --configuration large
NUM_LAYERS is 10
NUM_UNITS is 512
USE_SKIP_CONNECTIONS is True
LEARNING_RATE is 0.1
OPTIMIZER is adam

$ python group_example.py --configuration small
NUM_LAYERS is 3
NUM_UNITS is 32
USE_SKIP_CONNECTIONS is False
LEARNING_RATE is 0.1
OPTIMIZER is adam
```

We can also override individual settings in conjunction with groups. Individual settings take precedence over the group setting:

```console
$ python group_example.py --configuration large --num-units 768
NUM_LAYERS is 10
NUM_UNITS is 768
USE_SKIP_CONNECTIONS is True
LEARNING_RATE is 0.1
OPTIMIZER is adam
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

---

Btw, this has nothing to do with Chef's Effortless Config project, I forgot to google the name before I put it on pypi and now I guess I'm stuck with it.
