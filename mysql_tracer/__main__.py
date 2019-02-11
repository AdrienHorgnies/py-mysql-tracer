import argparse

import chest
from query import Query

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query')
    parser.add_argument('--host', required=True, help='MySQL Server host. Can be configured with mysql.host.')
    parser.add_argument('--user', required=True, help='MySQL Server user. Can be configured with mysql.user.')
    parser.add_argument('--database', help='MySQL database. Can be configured with mysql.database.')
    args = parser.parse_args()

    chest.host = args.host
    chest.user = args.user
    chest.database = args.database

    my_query = Query(args.query)
    print(my_query.query_str)
    print(my_query.result.execution_start)
    print(my_query.result.execution_end)
    print(my_query.result.duration)
    print(my_query.result.description)
    print(my_query.result.rows)
