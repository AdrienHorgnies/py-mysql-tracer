from mysql_tracer import _configuration
from mysql_tracer._query import Query
from mysql_tracer._cursor_provider import CursorProvider


def main():
    config = _configuration.get()

    CursorProvider(config['host'], config['user'], config['port'], config['database'], config['ask_password'],
                   config['store_password'])

    template_vars = config['template_vars'] if config['template_vars'] else []
    queries = [Query(path, dict(template_vars)) for path in config['query']]

    for query in queries:
        if config['display']:
            query.display()
        else:
            query.export(destination=config['destination'])


if __name__ == '__main__':
    main()
