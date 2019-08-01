from datetime import datetime, timedelta

import mock
import pytest

# noinspection PyProtectedMember
from mysql_tracer import _query


@pytest.fixture()
def cursor():
    mock_cursor = mock.Mock()
    mock_cursor.fetchall.return_value = [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    mock_cursor.description = (('name',), ('title',))

    return mock_cursor


@mock.patch('mysql_tracer._query.CursorProvider')
def test_executable_str(mock_cp, cursor):
    mock_cp.get.return_value = cursor

    actual = _query.Query('tests/assets/sample-query.sql')

    assert actual.executable_str == "SELECT name, title FROM person LEFT JOIN job " \
                                    "ON person.job_id = job.id WHERE title NOT IN ('developer');"


@mock.patch('mysql_tracer._query.CursorProvider')
def test_template_executable_str(mock_cp, cursor):
    mock_cp.get.return_value = cursor
    actual = _query.Query('tests/assets/sample-template-query.sql',
                          template_vars=dict(job='developer', disappear='', donotexist=''))

    assert actual.executable_str == "SELECT '{', '$jobs}', name, title FROM person LEFT JOIN job " \
                                    "ON person.job_id = job.id WHERE title IN ('developer') ;"


@mock.patch('mysql_tracer._query.CursorProvider')
@mock.patch('mysql_tracer._query.datetime')
def test_result(mock_datetime, mock_cp, cursor, asset):
    mock_cp.get.return_value = cursor
    mock_datetime.now.side_effect = (datetime(1992, 3, 4, 11, 0, 5, 654321),
                                     datetime(1992, 3, 4, 11, 0, 5, 987654))

    actual = _query.Query(asset('sample-query.sql')).result

    assert actual.execution_start == datetime(1992, 3, 4, 11, 0, 5, 654321)
    assert actual.execution_end == datetime(1992, 3, 4, 11, 0, 5, 987654)
    assert actual.execution_time == timedelta(microseconds=333333)
    assert actual.rows == [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    assert actual.description == ('name', 'title')
