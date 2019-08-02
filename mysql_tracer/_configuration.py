import configparser
import logging
from os import access, R_OK, X_OK
from pathlib import Path

log = logging.getLogger(__name__)

__user_config_path = Path.home().joinpath('.config', 'mysql-tracer', 'mysql-tracer.ini')


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
            log.debug('Found configuration file %s', __user_config_path)
            return __user_config_path
        else:
            raise PermissionError(__user_config_path)

    log.debug('Did not find configuration file')
    return None


def get():
    config_path = __find_config('mysql-tracer.ini')
    if config_path is None:
        return dict()

    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)
    return dict(config_parser.items('mysql_tracer'))
