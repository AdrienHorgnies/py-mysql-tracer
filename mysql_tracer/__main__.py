import argparse

from mysql_tracer import chest
from mysql_tracer._query import Query


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='+', help='Path to a file containing a single sql statement')
    parser.add_argument('--host', required=True, help='MySQL server host')
    parser.add_argument('--user', required=True, help='MySQL server user')
    parser.add_argument('--database', help='MySQL database name')
    parser.add_argument('-a', '--ask-password', default=False, action='store_true',
                        help='Do not try to retrieve password from keyring, always ask password')
    parser.add_argument('-s', '--store_password', default=False, action='store_true',
                        help='Store password into keyring after connecting to the database')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--destination', help='Directory where to export results')
    group.add_argument('--display', default=False, action='store_true',
                       help='Do not export results but display them to stdout')
    args = parser.parse_args()
    chest.host = args.host
    chest.user = args.user
    chest.database = args.database
    chest.ask_password = args.ask_password
    chest.store_password = args.store_password
    queries = [Query(path) for path in args.query]
    for query in queries:
        if not args.display:
            query.export(destination=args.destination)
        else:
            print(query.source)
            print(query.result.description)
            print(query.result.rows)


if __name__ == '__main__':
    main()
