import logging
from os import access, R_OK, X_OK
from pathlib import Path

log = logging.getLogger(__name__)

__user_config_path = Path.home().joinpath('.config', 'mysql-tracer', 'application.yml')
__configuration = None
__configured_help = '\nThis item is configured under {keys} with value `{value}`.' \
                    '\nSetting this option will override this value.'
__configurable_help = '\nThis item can be configured under {keys}.'


def __find_config(config_name):
    current_dir = Path.cwd()
    while access(str(current_dir), X_OK) and current_dir.parent is not current_dir:
        config_path = current_dir.joinpath(config_name)
        if config_path.exists():
            log.debug('Found configuration file %s', config_path)
            if access(str(config_path), R_OK):
                return config_path
            else:
                raise PermissionError(config_path)
        current_dir = current_dir.parent

    if __user_config_path.exists():
        if access(str(__user_config_path), R_OK):
            return __user_config_path
        else:
            raise PermissionError(__user_config_path)

    log.debug('Did not find configuration file')
    return None
