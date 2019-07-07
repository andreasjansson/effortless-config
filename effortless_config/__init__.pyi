# -*- mode: python -*-

from typing import TypeVar, Union, Optional, List

T = TypeVar('T', bound=Optional[Union[int, float, str, bool]])

def setting(default: T, **kwargs: T) -> T: ...

class Config:
    @classmethod
    def set_group(cls, group_name: str): ...
    @classmethod
    def parse_args(
        cls, argv: Optional[List[str]] = None, description: Optional[str] = None
    ): ...
    @classmethod
    def reset_to_defaults(cls): ...
    @classmethod
    def override(cls, **kwargs: T): ...
