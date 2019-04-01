import re
from datetime import datetime
from os.path import splitext, basename
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
        self.name = splitext(basename(source))[0]
        self.template_vars = template_vars if template_vars is not None else dict()
        self.interpolated = self.__interpolated()
        self.executable_str = self.__executable_str()
        self.result = Result(self.executable_str)

    def __repr__(self):
        return 'Query(' \
               'source={source!r}, ' \
               'name={name!r}, ' \
               'template_vars={template_vars!r}, ' \
               'interpolated={interpolated!r}, ' \
               'executable_str={executable_str!r}, ' \
               'result={result})'.format(**vars(self), interpolated=self.interpolated,
                                         executable_str=self.executable_str, result=self.result)

    def __interpolated(self):
        """
        String representation of the source file content after substituting template keys by their values and stripping
        line containing template keys that were not provided.

        :return: the content of the source file after template interpolation
        :rtype: str
        """
        template = Template(open(self.source).read())
        interpolated = template.safe_substitute(**self.template_vars)
        # remove lines for which template variables weren't provided
        return re.sub(r'\n.*\${\w+}.*', '', interpolated)

    def __executable_str(self):
        """
        Single line string representation of the query after interpolation

        :return: Single line string representation of the query after interpolation
        :rtype: str
        """
        return ' '.join([
            normalize_space(strip_inline_comment(line).strip())
            for line in self.interpolated.split('\n')
            if not is_comment(line) and not is_blank(line)
        ])

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

    def display(self):
        print('source: ' + self.source)
        print('sql: ' + self.executable_str)
        print('execution time: {}'.format(self.result.execution_time))
        print('rows count: {}'.format(len(self.result.rows)))
        print('description: {}'.format(self.result.description))
        for row in self.result.rows:
            print(row)


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
        self.execution_time = self.execution_end - self.execution_start
        self.rows = cursor.fetchall()
        self.description = tuple(column[0] for column in cursor.description)

    def __repr__(self):
        return 'Result(' \
               'execution_start={execution_start}, ' \
               'execution_end={execution_end}, ' \
               'execution_time={execution_time}, ' \
               'rows={rows}, ' \
               'description={description})'.format(**vars(self))
