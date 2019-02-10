from datetime import datetime, timedelta

import mock

import mysql_tracer


def test_query_str():
    tested_query = mysql_tracer.Query('tests/assets/sample-query.sql')

    assert tested_query.query_str == "SELECT name, title FROM person LEFT JOIN job " \
                                     "ON person.job_id = job.id WHERE title NOT IN ('developer');"


@mock.patch('mysql_tracer.query.CursorProvider')
@mock.patch('mysql_tracer.query.datetime')
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

    actual = mysql_tracer.Query('tests/assets/sample-query.sql').result

    assert actual.execution_start == datetime(1992, 3, 4, 11, 0, 5, 654321)
    assert actual.execution_end == datetime(1992, 3, 4, 11, 0, 5, 987654)
    assert actual.duration == timedelta(microseconds=333333)
    assert actual.rows == mock_cursor.fetchall.return_value
    assert actual.description == ('name', 'title')
