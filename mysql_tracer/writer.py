import csv
from os.path import join, dirname, basename, splitext
from shutil import copyfile


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

    copyfile(query.source, report_path)

    with open(report_path, 'a') as report_file:
        report_file.write(REPORT_TEMPLATE.format(
            start=query.result.execution_start.isoformat(),
            end=query.result.execution_end.isoformat(),
            duration=query.result.duration,
            count=len(query.result.rows),
            file=basename(export_path) if len(query.result.rows) > 0 else None
        ))

    if len(query.result.rows) > 0:
        with open(export_path, 'w') as export_file:
            csv_writer = csv.writer(export_file, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(query.result.description)
            for row in query.result.rows:
                csv_writer.writerow(row)

    return report_path, export_path
