from datetime import datetime, timedelta

import mock
import os.path

import query


def test_query_str():
    tested_query = query.Query('tests/assets/sample-query.sql')

    assert tested_query.query_str == "SELECT name, title FROM person LEFT JOIN job " \
                                     "ON person.job_id = job.id WHERE title NOT IN ('developer');"


def test_template_query_str():
    tested_query = query.Query('tests/assets/sample-template-query.sql',
                               template_vars=dict(job='developer', disappear='', donotexist=''))

    assert tested_query.query_str == "SELECT '{', '$jobs}', name, title FROM person LEFT JOIN job " \
                                     "ON person.job_id = job.id WHERE title IN ('developer') ;"


@mock.patch('query.CursorProvider')
@mock.patch('query.datetime')
def test_result(mock_datetime, mock_cp):
    mock_datetime.now.side_effect = (datetime(1992, 3, 4, 11, 0, 5, 654321),
                                     datetime(1992, 3, 4, 11, 0, 5, 987654))

    mock_cursor = mock.Mock()
    mock_cp.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    mock_cursor.description = (('name',), ('title',))

    actual = query.Query('tests/assets/sample-query.sql').result

    assert actual.execution_start == datetime(1992, 3, 4, 11, 0, 5, 654321)
    assert actual.execution_end == datetime(1992, 3, 4, 11, 0, 5, 987654)
    assert actual.duration == timedelta(microseconds=333333)
    assert actual.rows == mock_cursor.fetchall.return_value
    assert actual.description == ('name', 'title')


@mock.patch('query.CursorProvider')
@mock.patch('query.datetime')
def test_report(mock_datetime, mock_cp, query_path, executed_query_path):
    mock_datetime.now.side_effect = (datetime(1992, 3, 4, 11, 0, 5, 654321),
                                     datetime(1992, 3, 4, 11, 0, 5, 987654))

    mock_cursor = mock.Mock()
    mock_cp.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    mock_cursor.description = (('name',), ('title',))

    tested_query = query.Query(query_path)

    assert os.path.basename(tested_query.report) == '1992-03-04T11-00-05_query.sql'
    assert os.path.isfile(tested_query.report)
    assert [line for line in open(tested_query.report)] == [line for line in open(executed_query_path)]


@mock.patch('query.CursorProvider')
@mock.patch('query.datetime')
def test_export(mock_datetime, mock_cp, query_path, executed_export_path):
    mock_datetime.now.side_effect = (datetime(1992, 3, 4, 11, 0, 5, 654321),
                                     datetime(1992, 3, 4, 11, 0, 5, 987654))

    mock_cursor = mock.Mock()
    mock_cp.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    mock_cursor.description = (('name',), ('title',))

    tested_query = query.Query(query_path)

    assert os.path.basename(tested_query.export) == '1992-03-04T11-00-05_query.csv'
    assert os.path.isfile(tested_query.export)
    assert [line for line in open(tested_query.export)] == [line for line in open(executed_export_path)]
