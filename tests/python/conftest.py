import pytest
from os.path import join, abspath
from shutil import copy


RSRC = abspath(join('tests', 'assets'))


@pytest.fixture(scope='function')
def query_path(tmpdir_factory):
    tmp_query = tmpdir_factory.mktemp('test_ground').join('query.sql')
    copy(join(RSRC, 'sample-query.sql'), tmp_query)
    assert open(join(RSRC, 'sample-query.sql')).read() == open(tmp_query).read()
    return tmp_query


@pytest.fixture(scope='session')
def executed_query_path():
    return join(RSRC, 'sample-query-executed.sql')


@pytest.fixture(scope='session')
def executed_export_path():
    return join(RSRC, 'sample-query-executed.csv')
