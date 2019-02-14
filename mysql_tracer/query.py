import re
from datetime import datetime
from string import Template
from shutil import copyfile
import csv
from os import path

from cursor_provider import CursorProvider


REPORT_TEMPLATE = '''
-- START TIME: {start}
-- END TIME: {end}
-- DURATION: {duration}
-- ROWS COUNT: {count}
-- RESULT FILE: {file}
'''


class Query:

    def __init__(self, source, template_vars=None):
        self.source = source
        self.dir = path.dirname(source)
        self.basename = path.basename(source)
        self.raw_name, self.ext = path.splitext(self.basename)
        self.template_vars = template_vars if template_vars is not None else dict()
        self.__interpolated = None
        self.__query_str = None
        self.__result = None
        self.__report = None
        self.__export = None

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

    @property
    def report(self):
        if self.__report is not None:
            return self.__report
        else:
            prefix = self.result.execution_start.strftime("%Y-%m-%dT%H-%M-%S_")
            report_path = path.join(self.dir, prefix + self.basename)

            copyfile(self.source, report_path)

            with open(report_path, 'a') as executed_file:
                executed_file.write(REPORT_TEMPLATE.format(
                        start=self.result.execution_start.isoformat(),
                        end=self.result.execution_end.isoformat(),
                        duration=self.result.duration,
                        count=len(self.result.rows),
                        file=path.basename(self.export)
                ))

            self.__report = report_path
            return report_path

    @property
    def export(self):
        if self.__export is not None:
            return self.__export
        elif len(self.result.rows) == 0:
            return None
        else:
            prefix = self.result.execution_start.strftime("%Y-%m-%dT%H-%M-%S_")
            export_path = path.join(self.dir, prefix + self.raw_name + '.csv')

            with open(export_path, 'w') as export_file:
                csv_writer = csv.writer(export_file, quoting=csv.QUOTE_ALL)
                csv_writer.writerow(self.result.description)
                for row in self.result.rows:
                    csv_writer.writerow(row)

            self.__export = export_path
            return export_path


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
