import re
from datetime import datetime
from string import Template

from mysql_tracer import _writer as writer
from mysql_tracer._cursor_provider import CursorProvider


class Query:
    """
    Represents a MySQL query created from a file. The original file is never modified.

    The reason of existence of this class is to create traces of executed queries so you don't loose track of what you
    did.

    Implements a templating system using the syntax ${key}. Line containing a template key will be stripped from
    executed query if no substitute value is provided !

    Can execute said query and hold the results through the class Result.

    Properties are lazy evaluated and are evaluated only once. export and result trigger the execution of the query.
    """

    def __init__(self, source, template_vars=None):
        """
        :param source: the path to a file containing a single MySQL statement.
        :type source: str | os.PathLike
        :param template_vars: template keys and values to substitute. A Key ${key} will be replaced by the corresponding
         dictionary value.
        :type template_vars: dict
        """
        self.source = source
        self.template_vars = template_vars if template_vars is not None else dict()
        self.__interpolated = None
        self.__query_str = None
        self.__result = None

    @property
    def interpolated(self):
        """
        String representation of the source file content after substituting template keys by their values and stripping
        line containing template keys that were not provided.

        :return: the content of the source file after template interpolation
        :rtype: str
        """
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
        """
        Single line string representation of the query after interpolation

        :return: Single line string representation of the query after interpolation
        :rtype: str
        """
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
        """
        The result of the execution of the query, the value is processed at first access then retrieved every other
        times.

        :return: the result of the execution of the query
        :rtype: Result
        """
        if self.__result is not None:
            return self.__result
        else:
            self.__result = Result(self.query_str)
            return self.__result

    def export(self, destination=None):
        """
        Exports the query after interpolation to a file with a time prefixed version of the original file name with a
        mini report of the execution appended at the end of the file. And exports the result in a csv file with the same
        name except for the extension.

        :param destination: directory where to create the report and result files
        :type destination: str | os.PathLike
        :return: tuple(report, result)
        :rtype: tuple<str>
        """
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
    """
    Hold the results of the execution of a MySQL query

    execution_start: datetime before query execution
    execution_end: datetime after query execution
    duration: timedelta of execution_end minus execution_start
    rows: list<tuple<?>> the data the query fetched
    description: tuple<str> the headers of the rows
    """

    def __init__(self, query_str):
        """
        :param query_str: the query to execute
        :type query_str: str
        """
        cursor = CursorProvider.cursor()
        self.execution_start = datetime.now()
        cursor.execute(query_str)
        self.execution_end = datetime.now()
        self.duration = self.execution_end - self.execution_start
        self.rows = cursor.fetchall()
        self.description = tuple(column[0] for column in cursor.description)
