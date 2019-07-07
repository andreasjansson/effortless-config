import pkgutil

from effortless_config.config import Config
from effortless_config.config import Setting as setting

__version__ = (
    pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()  # type: ignore
)
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split('.'))
del pkgutil
