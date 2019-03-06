import argparse
import os.path
import re as __re
from pathlib import Path

import yaml

from mysql_tracer import chest

__user_config_path = Path.home().joinpath('.config', 'mysql-tracer', 'application.yml')
__configuration = None
__configured_help = '\nThis item is configured under {keys} with value `{value}`.' \
                    '\nSetting this option will override this value.'
__configurable_help = '\nThis item can be configured under {keys}.'


def __configure_yaml():
    home_matcher = __re.compile(r'\${home}')

    def home_constructor(loader, node):
        return home_matcher.sub(str(Path.home()), node.value)

    yaml.add_implicit_resolver('!home', home_matcher)
    yaml.add_constructor('!home', home_constructor)


__configure_yaml()


def __get_file_configuration(path=__user_config_path):
    if not os.path.exists(path):
        return dict()
    with open(str(path)) as config_file:
        return yaml.load(config_file)


def __add_configurable_argument(parser, configuration, keys, *args, **kwargs):
    """
    Add argument to parser but try to set default using provided configuration
    and set required to False if configuration does provide a value.
    Also append configuration file usage to help message.

    :param parser: to add an argument to
    :param configuration: which may contain argument value
    :param keys: which leads to corresponding argument value
    :param args: to pass to parser.add_argument method
    :param kwargs: to pass to parser.add_argument method
    :return: parser.add_argument(*args, **kwargs)
    :rtype: Action
    """
    item = configuration
    for key in keys:
        if key not in item:
            item = None
            break
        else:
            item = item[key]

    if 'required' in kwargs and item is not None:
        kwargs['required'] = False

    if item is not None:
        kwargs['help'] = kwargs['help'] + __configured_help.format(keys='.'.join(keys), value=item)
        kwargs['default'] = item
    else:
        kwargs['help'] = kwargs['help'] + __configurable_help.format(keys='.'.join(keys))

    return parser.add_argument(*args, **kwargs)


def __parse_args(configuration):
    description = 'CLI script to run queries and export results.' \
                  '\n\nSome items can be configured within file {}'.format(__user_config_path)

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    query = parser.add_argument_group(title='Queries')
    query.add_argument('query', nargs='+', help='Path to a file containing a single sql statement')
    query.add_argument('-t', '--template-var', dest='template_vars', nargs=2, metavar=('KEY', 'VALUE'),
                       action='append',
                       help='Define a key value pair to substitute the ${key} by the value within the query')

    db = parser.add_argument_group(title='Database')
    __add_configurable_argument(db, configuration, ['host'], '--host', required=True, help='MySQL server host')
    __add_configurable_argument(db, configuration, ['port'], '--port', required=False, default=3306, type=int,
                                help='MySQL server port')
    __add_configurable_argument(db, configuration, ['user'], '--user', required=True, help='MySQL server user')
    db.add_argument('--database', help='MySQL database name')

    pwd = parser.add_argument_group(title='Password')
    pwd.add_argument('-a', '--ask-password', default=False, action='store_true',
                     help='Do not try to retrieve password from keyring, always ask password')
    pwd.add_argument('-s', '--store-password', default=False, action='store_true',
                     help='Store password into keyring after connecting to the database')

    export = parser.add_argument_group(title='Export')
    excl_actions = export.add_mutually_exclusive_group()
    excl_actions.add_argument('-d', '--destination', help='Directory where to export results')
    excl_actions.add_argument('--display', default=False, action='store_true',
                              help='Do not export results but display them to stdout')
    args = parser.parse_args()

    configuration.update(vars(args))

    return configuration


def get():
    global __configuration
    if __configuration is None:
        __configuration = __parse_args(__get_file_configuration())

    return __configuration


def auto_configure():
    config = __get_file_configuration()

    chest.host = config.get('host')
    chest.port = config.get('port')
    chest.user = config.get('user')
    chest.database = config.get('database')
    chest.ask_password = config.get('ask_password')
    chest.store_password = config.get('store_password')
