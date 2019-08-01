import logging
from getpass import getpass

import keyring
from mysql import connector

log = logging.getLogger('mysql_tracer.CursorProvider')


class CursorProvider:

    connection = None

    def __init__(self, host, user, ask_password=False, store_password=False, port=3306, database=None):
        service = 'mysql-tracer/{host}'.format(host=host)

        keyring_password = None
        if ask_password:
            password = getpass('Password for {user}@{host}: '.format(user=user, host=host))
        else:
            log.debug('Retrieving password from keyring ({user}@{service})'.format(user=user, service=service))
            keyring_password = keyring.get_password(service, user)
            if keyring_password is None:
                log.info('Did not find password in keyring, asking for password...')
                password = getpass('Password for {user}@{host}: '.format(user=user, host=host))
            else:
                password = keyring_password

        log.debug('Trying to connect to the database {}@{}:{}/{}'.format(user, host, port, database))
        CursorProvider.connection = connector.connect(
            host=host,
            port=port,
            user=user,
            db=database,
            passwd=password)
        log.debug('Connection successful')

        if store_password and (keyring_password is None or password is not keyring_password):
            log.info('Storing password into keyring ({user}@{service})'.format(user=user, service=service))
            keyring.set_password(service, user, password)
            if keyring.get_password(service, user) is password:
                log.info('Successfully stored password into keyring')
            else:
                log.error('Failed to store password into keyring')

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()

    @staticmethod
    def get():
        assert CursorProvider.connection is not None, 'You must initialize CursorProvider before using it'
        return CursorProvider.connection.cursor()
