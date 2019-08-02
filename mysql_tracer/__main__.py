import argparse
import logging

from mysql_tracer import _configuration
from mysql_tracer._cursor_provider import CursorProvider
from mysql_tracer._query import Query

log = logging.getLogger('mysql_tracer')


def __parse_args(parents, remaining_args, defaults):
    description = 'CLI script to run queries and export results.'

    parser = argparse.ArgumentParser(parents=parents,
                                     description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.set_defaults(**{
        'port': 3306,
        **defaults
    })

    query = parser.add_argument_group(title='Queries')
    query.add_argument('query', nargs='+', help='Path to a file containing a single sql statement')
    query.add_argument('-t', '--template-var', dest='template_vars', nargs=2, metavar=('KEY', 'VALUE'),
                       action='append',
                       help='Define a key value pair to substitute the ${key} by the value within the query')

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

    export = parser.add_argument_group(title='Export')
    excl_actions = export.add_mutually_exclusive_group()
    excl_actions.add_argument('-d', '--destination', help='Directory where to export results')
    excl_actions.add_argument('--display', action='store_true', help='Do not export results but display them to stdout')

    for action in parser._actions:
        if action.required and action.default is not None:
            action.required = False

    args = parser.parse_args(remaining_args)
    print(args)  # todo remove me
    return args


def __parse_log_args():
    log_args_parser = argparse.ArgumentParser(add_help=False)
    log_args_parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    log_args, remaining_args = log_args_parser.parse_known_args()

    if log_args.log_level is not None:
        log.setLevel(log_args.log_level)
        console = logging.StreamHandler()
        console.setLevel(log_args.log_level)
        console.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s - %(name)s: %(message)s'))
        log.addHandler(console)

    return log_args_parser, remaining_args


def main():
    log_args_parsers, remaining_args = __parse_log_args()
    config = _configuration.get()
    args = __parse_args([log_args_parsers], remaining_args, config)

    CursorProvider.init(args.host, args.user, args.port, args.database, args.ask_password,
                        args.store_password)

    template_vars = args.template_vars if args.template_vars else []
    queries = [Query(path, dict(template_vars)) for path in args.query]

    for query in queries:
        if args.display:
            query.display()
        else:
            query.export(destination=args.destination)


if __name__ == '__main__':
    # log.setLevel(logging.DEBUG)
    # sh = logging.StreamHandler()
    # sh.setLevel(logging.DEBUG)
    # sh.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s - %(name)s: %(message)s'))
    # log.addHandler(sh)

    main()
