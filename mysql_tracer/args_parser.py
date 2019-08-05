"""
CLI script to run MySQL SELECT statements

It produces a copy of provided file with additional metadata and an export of results in CSV format
"""
import argparse


def get_main_args_parser(parents, defaults):
    """
    Parser for the arguments required to run mysql_tracer.

    :param parents: a list of parent argument parsers. They must NOT define a help option or else they will clash.
    :param defaults: a dictionary with default values. All actions with default values are set to not required.
    :return: an argument parser
    """
    parser = argparse.ArgumentParser(parents=parents + [get_database_args_parser()],
                                     description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.set_defaults(**{
        'port': 3306,
        **defaults
    })

    query = parser.add_argument_group(title='Queries')
    query.add_argument('query', nargs='+', help='Path to a file containing a single sql statement')

    export = parser.add_argument_group(title='Export')
    excl_actions = export.add_mutually_exclusive_group()
    excl_actions.add_argument('-d', '--destination', help='Directory where to export results')
    excl_actions.add_argument('--display', action='store_true', help='Do not export results but display them to stdout')

    # noinspection PyProtectedMember
    for action in parser._actions:
        if action.required and action.default is not None:
            action.required = False

    return parser


def get_database_args_parser():
    parser = argparse.ArgumentParser(add_help=False)

    db = parser.add_argument_group(title='Database')
    db.add_argument('--host', required=True, help='MySQL server host')
    db.add_argument('--port', type=int, help='MySQL server port')
    db.add_argument('--user', required=True, help='MySQL database user')
    db.add_argument('--database', help='MySQL database name')

    pwd = parser.add_argument_group(title='Password')
    pwd.add_argument('-a', '--ask-password', action='store_true',
                     help='Ask password; do not try to retrieve password from keyring')
    pwd.add_argument('-s', '--store-password', action='store_true',
                     help='Store password into keyring after connecting to the database')

    return parser


def get_log_args_parser():
    """
    Parser for the arguments required to set logger level

    :return: an argument parser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Verbosity level of the logger')

    return parser