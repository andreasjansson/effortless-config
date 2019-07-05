import sys
import re
from abc import ABCMeta
import argparse
from typing import List, Dict, Union, Optional, Type

SUPPORTED_TYPES = [int, float, str, bool, type(None)]
SettingType = Optional[Union[int, float, str, bool]]
SETTING_NAME_REGEX = re.compile('[A-Z][A-Z0-9_]*')


class Setting:
    def __init__(self, default: SettingType, **kwargs: SettingType):
        """
        Create a new configurable parameter, inside a class that extends Config.

        Args:
            default: Default parameter value.
            **kwargs: Map of group name to group value.

        Returns:
            A new setting.
        """
        self.default = default
        self.group_values = kwargs
        self.type: Type[SettingType]

        if default is None:
            if self.group_values:
                self.type = _get_common_type(list(kwargs.values()))
            else:
                self.type = str  # default to string if everything else fails
        else:
            self.type = type(default)

        if self.type not in SUPPORTED_TYPES:
            raise ValueError(
                '{type} is not a supported type, only '
                '{supported_types} are supported.'.format(
                    type=self.type, supported_types=SUPPORTED_TYPES
                )
            )


class ConfigMeta(ABCMeta):

    _settings: Dict[str, Setting] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        new_namespace = {}

        groups = namespace.get('groups', [])

        for key, value in namespace.items():
            if isinstance(value, Setting):
                if not SETTING_NAME_REGEX.match(key):
                    raise ValueError('Settings must be in the format [A-Z][A-Z0-9_]*')

                undefined_groups = set(value.group_values.keys()) - set(groups)
                if undefined_groups:
                    raise ValueError(
                        'Undefined groups: {undefined_groups}, '
                        'did you set `groups = [...]` in your config class?'.format(
                            undefined_groups=undefined_groups
                        )
                    )

                mcs._settings[key] = value
                new_namespace[key] = value.default
            else:
                new_namespace[key] = value

        return super().__new__(mcs, name, bases, new_namespace, **kwargs)


class Config(metaclass=ConfigMeta):

    groups: List[str]

    def __init__(self):
        """
        Don't instantiate Config objects, everything works at the class level.
        """
        raise ValueError('Config class can not be instantiated')

    @classmethod
    def set_group(cls, group_name: str):
        """
        Set the configuration values to a specific group.

        Args:
            group_name: The name of the group.
        """
        for name, setting in cls._settings.items():
            if group_name in setting.group_values:
                setattr(cls, name, setting.group_values[group_name])
            else:
                setattr(cls, name, setting.default)

    @classmethod
    def parse_args(
        cls, argv: Optional[List[str]] = None, description: Optional[str] = None
    ):
        """
        Parse configuration from the command line, falling back to defaults
        where arguments are not given.

        Args:
            argv: List of command line arguments, e.g. sys.argv[1] (optional).
            description: Text to pass to argparse.ArgumentParser (optional).
        """
        if argv is None:
            argv = sys.argv[1:]

        parser = argparse.ArgumentParser(description=description)

        parser.add_argument('--configuration', '-c', choices=cls.groups)

        for name, setting in cls._settings.items():
            option = _config_name_to_option(name)
            if setting.type == bool:
                parser.add_argument(option, type=str, choices=['true', 'false'])
            else:
                parser.add_argument(option, type=setting.type)

        args = parser.parse_args(argv)

        if args.configuration:
            cls.set_group(args.configuration)

        for name, setting in cls._settings.items():
            arg_name = _config_name_to_arg_name(name)
            arg_value = getattr(args, arg_name)
            if arg_value is not None:
                if setting.type == bool:
                    setattr(cls, name, arg_value == 'true')
                else:
                    setattr(cls, name, arg_value)

    @classmethod
    def reset_to_defaults(cls):
        """
        Reset all settings to their default values.
        """
        for name, setting in cls._settings.items():
            setattr(cls, name, setting.default)

    @classmethod
    def override(cls, **kwargs: SettingType):
        """
        Override specific settings. Useful in testing. Can optionally be used
        as a context manager, which will automatically reset to the previous state.
        """
        return _OverrideContextManager(cls, overrides=kwargs)


class _OverrideContextManager:

    # pylint:disable=protected-access
    def __init__(self, cls, overrides: Dict[str, SettingType]):
        self.cls = cls
        self.original_values: Dict[str, SettingType] = {}

        for key, value in overrides.items():
            if not hasattr(self.cls, key):
                raise ValueError('Unknown config flag: {key}'.format(key=key))

            original_value = getattr(self.cls, key)
            self.original_values[key] = original_value
            setattr(self.cls, key, value)

    def __enter__(self):
        return

    # pylint:disable=redefined-builtin
    def __exit__(self, type, value, traceback):
        for key, val in self.original_values.items():
            setattr(self.cls, key, val)


def _config_name_to_arg_name(name):
    return name.lower()


def _config_name_to_option(name):
    return '--' + name.lower().replace('_', '-')


def _get_common_type(values: List[SettingType]) -> Type[SettingType]:
    first_type = type(values[0])
    other_types = [type(v) for v in values[1:]]
    if all([first_type == t for t in other_types]):  # type: ignore
        return first_type
    raise ValueError(
        'Not all values have the same type: {values}'.format(values=values)
    )
