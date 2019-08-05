import csv
import logging
from os.path import join, dirname, basename, splitext, realpath

log = logging.getLogger('mysql_tracer.writer')

REPORT_TEMPLATE = '''
-- START TIME: {start}
-- END TIME: {end}
-- DURATION: {duration}
-- ROWS COUNT: {count}
-- RESULT FILE: {file}
'''


def write(query, destination=None):
    prefix = query.result.execution_start.strftime("%Y-%m-%dT%H-%M-%S_")

    directory = destination if destination is not None else dirname(query.source)
    report_path = join(directory, prefix + basename(query.source))
    export_path = splitext(report_path)[0] + '.csv'

    log.debug('Writing report for single query {} to {}'.format(query.name, realpath(directory)))

    with open(report_path, 'w') as report_file:
        report_file.writelines(open(query.source))
        report_file.write(REPORT_TEMPLATE.format(
            start=query.result.execution_start.isoformat(),
            end=query.result.execution_end.isoformat(),
            duration=query.result.execution_time,
            count=len(query.result.rows),
            file=basename(export_path) if len(query.result.rows) > 0 else None
        ))

    if len(query.result.rows) > 0:
        with open(export_path, 'w') as export_file:
            log.debug('Exporting results to {}'.format(export_path))
            csv_writer = csv.writer(export_file, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(query.result.description)
            for row in query.result.rows:
                csv_writer.writerow(row)

    return report_path, export_path
