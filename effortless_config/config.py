import sys
import re
from abc import ABCMeta
import argparse
from typing import List, Dict, Union, Optional, Type

from effortless_config import base62


SUPPORTED_TYPES = [int, float, str, bool, type(None)]
SettingType = Optional[Union[int, float, str, bool]]
SETTING_FORMAT = '[A-Z][A-Z0-9_]*'


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
    def __new__(mcs, name, bases, namespace, **kwargs):
        classcell = namespace.pop('__classcell__', None)
        new_namespace = {}

        groups = namespace.get('groups', [])
        new_namespace['groups'] = groups

        settings = namespace.get('_settings', {})
        new_namespace['_settings'] = settings

        for key, value in namespace.items():
            if key == 'groups':
                continue

            elif isinstance(value, Setting):
                _validate_setting_key(key)
                undefined_groups = set(value.group_values.keys()) - set(groups)
                if undefined_groups:
                    raise ValueError(
                        'Undefined groups: {undefined_groups}, '
                        'did you set `groups = [...]` in your config class?'.format(
                            undefined_groups=undefined_groups
                        )
                    )

                settings[key] = value
                new_namespace[key] = value.default

            elif (
                not callable(value)
                and not key.startswith('_')
                and key not in settings
                and not isinstance(value, classmethod)
            ):
                _validate_setting_key(key)
                settings[key] = Setting(default=value)
                new_namespace[key] = value

            else:
                new_namespace[key] = value

        if classcell is not None:
            new_namespace['__classcell__'] = classcell

        return super().__new__(mcs, name, bases, new_namespace, **kwargs)

    def to_hash_string(cls):
        return base62.encode(abs(hash(cls)))

    def __str__(cls):
        return repr(cls)

    def __repr__(cls):
        lines = [f'class {cls.__name__}(Config):']
        if cls.groups:
            lines += [f'    groups = {repr(cls.groups)}']
        for key in cls._settings:
            lines += [f'    {key} = {repr(getattr(cls, key))}']

        return '\n'.join(lines)

    def __hash__(cls):
        values = tuple([getattr(cls, key) for key in sorted(cls._settings)])
        return hash(values)

    def __eq__(cls, other):
        return isinstance(other, ConfigMeta) and hash(other) == hash(cls)


class Config(metaclass=ConfigMeta):

    groups: List[str]
    _settings: Dict[str, Setting]

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
        if group_name not in cls.groups:
            raise ValueError(f'Unknown group: {group_name}')

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

        if cls.groups:
            parser.add_argument(
                '--configuration',
                '-c',
                choices=['default'] + cls.groups,
                default='default',
            )

        for name, setting in cls._settings.items():
            option = _config_name_to_option(name)
            if setting.type == bool:
                parser.add_argument(option, type=str, choices=['true', 'false'])
            else:
                parser.add_argument(option, type=setting.type)

        args = parser.parse_args(argv)

        if cls.groups:
            if args.configuration == 'default':
                cls.reset_to_defaults()
            else:
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


def _validate_setting_key(key: str):
    if not re.match(SETTING_FORMAT, key):
        raise ValueError(f'Settings must be in the format {SETTING_FORMAT}')
