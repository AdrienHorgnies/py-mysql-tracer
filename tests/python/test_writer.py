from datetime import datetime, timedelta
from os.path import isfile, basename, join

import mock
import pytest

# noinspection PyProtectedMember
from mysql_tracer import _writer


@pytest.fixture
def query(asset, asset_copy):
    query_mock = mock.MagicMock()
    query_mock.source = asset_copy('sample-query-with-easy-template.sql')
    query_mock.interpolated = open(asset('sample-query.sql')).read()
    query_mock.result = mock.MagicMock()
    query_mock.result.execution_start = datetime(1992, 3, 4, 11, 0, 5, 654321)
    query_mock.result.execution_end = datetime(1992, 3, 4, 11, 0, 5, 987654)
    query_mock.result.duration = timedelta(microseconds=333333)
    query_mock.result.rows = [
        ('Adrien Horgnies', 'analyst developer'),
        ('Constance de Lannoy', 'secretary')
    ]
    query_mock.result.description = ('name', 'title')
    return query_mock


def test_write(query, executed_query_path, executed_export_path):
    report, export = _writer.write(query)

    assert basename(report) == '1992-03-04T11-00-05_query.sql'
    assert isfile(report)
    assert [line for line in open(report)] == [line for line in open(executed_query_path)]
    
    assert basename(export) == '1992-03-04T11-00-05_query.csv'
    assert isfile(export)
    assert [line for line in open(export)] == [line for line in open(executed_export_path)]


def test_write_with_destination(query, tmpdir, executed_query_path, executed_export_path):
    report, export = _writer.write(query, tmpdir)

    assert report == join(tmpdir, '1992-03-04T11-00-05_query.sql')
    assert export == join(tmpdir, '1992-03-04T11-00-05_query.csv')
    assert isfile(report)
    assert isfile(export)
    assert [line for line in open(report)] == [line for line in open(executed_query_path)]
    assert [line for line in open(export)] == [line for line in open(executed_export_path)]
