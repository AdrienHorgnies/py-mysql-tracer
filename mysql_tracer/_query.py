import logging
import re
from datetime import datetime
from os.path import splitext, basename

from mysql_tracer import _writer as writer
from mysql_tracer.cursor_provider import CursorProvider

q_log = logging.getLogger('mysql_tracer.Query')
r_log = logging.getLogger('mysql_tracer.Result')


class Query:
    """
    Represents a MySQL query created from a file. The original file is never modified.

    The reason of existence of this class is to create traces of executed queries so you don't loose track of what you
    did.

    Can execute said query and hold the results through the class Result.
    """

    def __init__(self, source):
        """
        :param source: the path to a file containing a single MySQL statement.
        :type source: str | os.PathLike
        """
        q_log.debug('Initiating Query(source={!r})'.format(source))
        self.source = source
        self.name = splitext(basename(source))[0]
        self.executable_str = self.__executable_str()
        self.result = Result(self.executable_str)
        q_log.debug('Initiated Query(name={!r})'.format(self.name))

    def __repr__(self):
        return 'Query(' \
               'source={source!r}, ' \
               'name={name!r}, ' \
               'executable_str={executable_str!r}, ' \
               'result={result})'.format(**vars(self))

    def __executable_str(self):
        """
        Single line string representation of the query without comments
        """
        query_text = ' '.join([re.sub('(--|#).*', '', line) for line in open(self.source)])
        query_text = re.sub(r'\s+', ' ', query_text)
        return query_text.strip()

    def export(self, destination=None):
        """
        Exports the query to a file with a time prefixed version of the original file name with a
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
        cursor = CursorProvider.get()
        r_log.info('Executing %s', query_str)
        self.execution_start = datetime.now()
        cursor.execute(query_str)
        self.execution_end = datetime.now()
        self.execution_time = self.execution_end - self.execution_start
        self.rows = cursor.fetchall()
        r_log.debug('Got %d row(s)', len(self.rows))
        self.description = tuple(column[0] for column in cursor.description)

    def __repr__(self):
        return 'Result(' \
               'execution_start={execution_start}, ' \
               'execution_end={execution_end}, ' \
               'execution_time={execution_time}, ' \
               'rows={rows}, ' \
               'description={description})'.format(**vars(self))
