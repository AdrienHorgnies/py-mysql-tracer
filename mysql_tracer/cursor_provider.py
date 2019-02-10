from getpass import getpass

from alone import MetaSingleton
from mysql import connector
import keyring

from mysql_tracer.chest import host, user, database


class CursorProvider(metaclass=MetaSingleton):

    def __init__(self):
        service = 'CursorProvider-{host}'.format(host=host, db=database)
        keyring_password = keyring.get_password(service, user)
        if keyring_password is None:
            password = getpass("Password for {user}@{host}: ".format(user=user, host=host, db=database))
        else:
            password = keyring_password

        self.connection = connector.connect(
            host=host,
            user=user,
            db=database,
            passwd=password)

        if password is not keyring_password:
            keyring.set_password(service, user, password)

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()

    @staticmethod
    def cursor():
        return CursorProvider().connection.cursor()

    @staticmethod
    def add_arguments_to(parser):
        parser.add_argument("--host", required=True, help="MySQL Server host. Can be configured with mysql.host.",
                            conf_key="mysql.host")
        parser.add_argument("--user", required=True, help="MySQL Server user. Can be configured with mysql.user.",
                            conf_key="mysql.user")
