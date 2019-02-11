import re
from datetime import datetime

from cursor_provider import CursorProvider


class Query:

    def __init__(self, source):
        self.source = source
        self.__query_str = None
        self.__result = None

    @property
    def query_str(self):
        if self.__query_str is not None:
            return self.__query_str
        else:
            self.__query_str = ' '.join([
                normalize_space(strip_inline_comment(line).strip())
                for line in open(self.source)
                if not is_comment(line) and not is_blank(line)
            ])
            return self.__query_str

    @property
    def result(self):
        if self.__result is not None:
            return self.__result
        else:
            self.__result = Result(self.query_str)
            return self.__result


def normalize_space(line):
    return re.sub(' +', ' ', line)


def strip_inline_comment(line):
    return re.sub('(--|#).*', '', line)


def is_blank(line):
    return not line.strip()


def is_comment(line):
    return line.strip().startswith('--') or line.strip().startswith('#')


class Result:

    def __init__(self, query_str):
        cursor = CursorProvider.cursor()
        self.execution_start = datetime.now()
        cursor.execute(query_str)
        self.execution_end = datetime.now()
        self.duration = self.execution_end - self.execution_start
        self.rows = cursor.fetchall()
        self.description = tuple(column[0] for column in cursor.description)
