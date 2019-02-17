import re
from datetime import datetime
from string import Template

import writer
from cursor_provider import CursorProvider


class Query:

    def __init__(self, source, template_vars=None):
        self.source = source
        self.template_vars = template_vars if template_vars is not None else dict()
        self.__interpolated = None
        self.__query_str = None
        self.__result = None

    @property
    def interpolated(self):
        if self.__interpolated is not None:
            return self.__interpolated
        else:
            template = Template(open(self.source).read())
            interpolated = template.safe_substitute(**self.template_vars)
            unprovided_filtered = re.sub('\n.*\\${\\w+}.*\n', '\n', interpolated)
            self.__interpolated = unprovided_filtered
            return self.__interpolated

    @property
    def query_str(self):
        if self.__query_str is not None:
            return self.__query_str
        else:
            self.__query_str = ' '.join([
                normalize_space(strip_inline_comment(line).strip())
                for line in self.interpolated.split('\n')
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

    def export(self, destination=None):
        return writer.write(self, destination)


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
