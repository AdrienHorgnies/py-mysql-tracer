"""
Handle finding and parsing configuration file
"""
import configparser
import logging
from os import access, R_OK, X_OK
from pathlib import Path

log = logging.getLogger(__name__)

__mysql_tracer_ini = 'mysql-tracer.ini'
__user_config_path = Path.home().joinpath('.config', 'mysql-tracer', __mysql_tracer_ini)


def __find_config(config_name):
    """
    Search for a configuration file.

    First it searches current directory and above and then at user configuration folder

    :param config_name: name of the configuration file
    :return: path to the configuration file if it is found, else None
    :rtype Path | NoneType
    """
    current_dir = Path.cwd()
    while access(str(current_dir), X_OK) and current_dir.parent is not current_dir:
        config_path = current_dir.joinpath(config_name)
        log.debug('Searching configuration file at %s', config_path)
        if config_path.exists():
            log.debug('Found configuration file %s', config_path)
            if access(str(config_path), R_OK):
                return config_path
            else:
                raise PermissionError(config_path)
        current_dir = current_dir.parent

    log.debug('Searching configuration file at %s', __user_config_path)
    if __user_config_path.exists():
        if access(str(__user_config_path), R_OK):
            log.debug('Found configuration file %s', __user_config_path)
            return __user_config_path
        else:
            raise PermissionError(__user_config_path)

    log.debug('Did not find configuration file')
    return None


def get():
    config_path = __find_config(__mysql_tracer_ini)
    if config_path is None:
        return dict()

    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)
    return dict(config_parser.items('mysql_tracer'))
