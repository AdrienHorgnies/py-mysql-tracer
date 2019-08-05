import logging
from getpass import getpass

import keyring
from mysql import connector
from mysql.connector.errors import ProgrammingError

log = logging.getLogger(__name__)


class CursorProvider:
    instance = None

    @classmethod
    def get(cls):
        if CursorProvider.instance is None:
            raise AttributeError('Trying to get instance before instantiating, call {} from {}.{} beforehand'
                                 .format(CursorProvider.init.__name__, __name__, cls.__name__))
        return CursorProvider.instance.connection.cursor()

    @staticmethod
    def init(host, user, port=None, database=None, ask_password=False, store_password=False):
        CursorProvider.instance = CursorProvider.__CursorProvider(host, user, port, database, ask_password,
                                                                  store_password)

    class __CursorProvider:

        def __init__(self, host, user, port=None, database=None, ask_password=False, store_password=False):
            port = port if port is not None else 3306
            log.debug('Trying to connect to the database %s@%s:%s/%s', user, host, port, database)

            service = 'mysql-tracer/{host}'.format(host=host)

            if ask_password:
                self.connect_with_retry(host, port, user, database, service, store_password)
            else:
                log.debug('Retrieving password from keyring (%s@%s)', user, service)
                keyring_password = keyring.get_password(service, user)

                if keyring_password is not None:
                    self.connection = connector.connect(host=host, port=port, user=user, db=database,
                                                        password=keyring_password)
                else:
                    log.info('Did not find password in keyring, asking for password...')
                    self.connect_with_retry(host, port, user, database, service, store_password)

            log.info('Connected to database with success')

        def connect_with_retry(self, host, port, user, database, service, store_password, retry=2):
            password = getpass('Password for {user}@{host}: '.format(user=user, host=host))

            try:
                self.connection = connector.connect(host=host, port=port, user=user, db=database, password=password)
            except ProgrammingError as error:
                if error.errno == 1045 and retry > 0:
                    log.warning('Access Denied, retrying...')
                    self.connect_with_retry(host, port, user, database, service, store_password, retry=retry - 1)
                else:
                    raise error

            if store_password:
                log.info('Storing password into keyring (%s@%s)', user, service)
                keyring.set_password(service, user, password)

        def __del__(self):
            if hasattr(self, 'connection') and self.connection.is_connected():
                log.info('Closing connection to database')
                self.connection.close()
