import argparse
import logging

from mysql_tracer._cursor_provider import CursorProvider
from mysql_tracer._query import Query

log = logging.getLogger('mysql_tracer')


def __parse_args():
    description = 'CLI script to run queries and export results.'

    log_args_parser = get_log_level_args_parser()

    log_args, remaining_args = log_args_parser.parse_known_args()

    if log_args.log_level is not None:
        log.setLevel(log_args.log_level)
        console = logging.StreamHandler()
        console.setLevel(log_args.log_level)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s - %(name)s: %(message)s'))
        log.addHandler(console)

    parser = argparse.ArgumentParser(parents=[log_args_parser],
                                     description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    query = parser.add_argument_group(title='Queries')
    query.add_argument('query', nargs='+', help='Path to a file containing a single sql statement')
    query.add_argument('-t', '--template-var', dest='template_vars', nargs=2, metavar=('KEY', 'VALUE'),
                       action='append',
                       help='Define a key value pair to substitute the ${key} by the value within the query')

    db = parser.add_argument_group(title='Database')
    db.add_argument('--host', required=True, help='MySQL server host')
    db.add_argument('--port', required=False, default=3306, type=int,
                    help='MySQL server port')
    db.add_argument('--user', required=True, help='MySQL database user')
    db.add_argument('--database', help='MySQL database name')

    pwd = parser.add_argument_group(title='Password')
    pwd.add_argument('-a', '--ask-password', default=False, action='store_true',
                     help='Ask password; do not try to retrieve password from keyring')
    pwd.add_argument('-s', '--store-password', default=False, action='store_true',
                     help='Store password into keyring after connecting to the database')

    export = parser.add_argument_group(title='Export')
    excl_actions = export.add_mutually_exclusive_group()
    excl_actions.add_argument('-d', '--destination', help='Directory where to export results')
    excl_actions.add_argument('--display', default=False, action='store_true',
                              help='Do not export results but display them to stdout')

    log_args = parser.parse_args(remaining_args)

    return vars(log_args)


def get_log_level_args_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    return parser


def main():
    # todo implement configuration file handling
    # config = _configuration.__find_config(__name__)
    config = __parse_args()
    # if config is None:
    #     args = __parse_args()

    CursorProvider.init(config['host'], config['user'], config['port'], config['database'], config['ask_password'],
                        config['store_password'])

    template_vars = config['template_vars'] if config['template_vars'] else []
    queries = [Query(path, dict(template_vars)) for path in config['query']]

    for query in queries:
        if config['display']:
            query.display()
        else:
            query.export(destination=config['destination'])


if __name__ == '__main__':
    # log.setLevel(logging.DEBUG)
    # sh = logging.StreamHandler()
    # sh.setLevel(logging.DEBUG)
    # sh.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s - %(name)s: %(message)s'))
    # log.addHandler(sh)

    main()
