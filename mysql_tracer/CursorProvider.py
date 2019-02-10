import getpass

from alone import MetaSingleton
from mysql import connector

from chest import host, user, database


class CursorProvider(metaclass=MetaSingleton):

    def __init__(self):
        self.connection = connector.connect(
            host=host,
            user=user,
            db=database,
            passwd=getpass.getpass(
                "Password for {user}@{host}/{db}: ".format(user=user, host=host, db=database))
        )

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
