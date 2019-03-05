import configuration
from mysql_tracer import chest
from mysql_tracer._query import Query


def main():
    config = configuration.get()

    chest.host = config['host']
    chest.port = config['port']
    chest.user = config['user']
    chest.database = config['database']
    chest.ask_password = config['ask_password']
    chest.store_password = config['store_password']

    template_vars = config['template_vars'] if config['template_vars'] else None
    queries = [Query(path, dict(template_vars)) for path in config['query']]
    for query in queries:
        if config['display']:
            print(query)
        else:
            query.export(destination=config['destination'])


if __name__ == '__main__':
    main()
