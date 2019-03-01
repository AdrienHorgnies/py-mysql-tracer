from os.path import join, dirname, realpath
from shutil import copy

import pytest

RSRC = join(dirname(realpath(__file__)), 'tests', 'assets')


@pytest.fixture(scope='function')
def query_path(tmpdir_factory):
    tmp_query = tmpdir_factory.mktemp('test_ground').join('query.sql')
    copy(join(RSRC, 'sample-query.sql'), tmp_query)
    assert open(join(RSRC, 'sample-query.sql')).read() == open(tmp_query).read()
    return tmp_query


@pytest.fixture(scope='session')
def asset_copy(tmpdir_factory):
    def __copy(*args):
        copy_path = tmpdir_factory.mktemp('test_ground').join(args[-1])
        copy(join(RSRC, *args), copy_path)
        return copy_path

    return __copy


@pytest.fixture(scope='session')
def asset():
    def __get(*args):
        return join(RSRC, *args)

    return __get


@pytest.fixture(scope='session')
def executed_query_path():
    return join(RSRC, 'sample-query-executed.sql')


@pytest.fixture(scope='session')
def executed_export_path():
    return join(RSRC, 'sample-query-executed.csv')
