from os.path import join, dirname, realpath
from shutil import copy

import pytest

RSRC = join(dirname(realpath(__file__)), 'tests', 'assets')


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
