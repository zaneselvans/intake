import os
import pytest
from intake.catalog.local import LocalCatalogEntry, UserParameter
from intake.source.base import DataSource


class NoSource(DataSource):

    def __init__(self, **kwargs):
        self.kwargs = kwargs


driver = 'intake.catalog.tests.test_parameters.NoSource'


def test_simplest():
    e = LocalCatalogEntry('', '', driver, args={'arg1': 1})
    s = e()
    assert s.kwargs['arg1'] == 1


def test_parameter_default():
    up = UserParameter('name', default='oi')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up])
    s = e()
    assert s.kwargs['arg1'] == 'oi'


def test_maybe_par_env():
    up = UserParameter('name', default='env(INTAKE_TEST_VAR)')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up], getenv=False)
    s = e()
    assert s.kwargs['arg1'] == 'env(INTAKE_TEST_VAR)'

    os.environ['INTAKE_TEST_VAR'] = 'oi'
    up = UserParameter('name', default='env(INTAKE_TEST_VAR)')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up])
    s = e()
    assert s.kwargs['arg1'] == 'oi'

    del os.environ['INTAKE_TEST_VAR']

    s = e()
    assert s.kwargs['arg1'] == ''


def test_up_averride():
    up = UserParameter('name', default='env(INTAKE_TEST_VAR)')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up], getenv=False)
    s = e(name='other')
    assert s.kwargs['arg1'] == 'other'


def test_override():
    up = UserParameter('name', default='env(INTAKE_TEST_VAR)')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up], getenv=False)
    s = e(arg1='other')
    assert s.kwargs['arg1'] == 'other'


def test_auto_env():
    os.environ['INTAKE_TEST_VAR'] = 'oi'
    e = LocalCatalogEntry('', '', driver,
                          args={'arg1': "{{env(INTAKE_TEST_VAR)}}"},
                          parameters=[], getenv=True)
    s = e()
    assert s.kwargs['arg1'] == 'oi'

    del os.environ['INTAKE_TEST_VAR']

    s = e()
    assert s.kwargs['arg1'] == ''

    e = LocalCatalogEntry('', '', driver,
                          args={'arg1': "{{env(INTAKE_TEST_VAR)}}"},
                          parameters=[], getenv=False)
    s = e()
    assert s.kwargs['arg1'] == '{{env(INTAKE_TEST_VAR)}}'


def test_validate_up():
    up = UserParameter('name', default=1, type='int')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up], getenv=False)
    e()  # OK
    with pytest.raises(ValueError):
        e(name='oi')

    up = UserParameter('name', type='int')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"},
                          parameters=[up], getenv=False)
    s = e()  # OK
    assert s.kwargs['arg1'] == '0'  # default default for int


def test_validate_par():
    up = UserParameter('arg1', type='int')
    e = LocalCatalogEntry('', '', driver, args={'arg1': "oi"},
                          parameters=[up], getenv=False)
    with pytest.raises(ValueError):
        e()
    e = LocalCatalogEntry('', '', driver, args={'arg1': 1},
                          parameters=[up], getenv=False)
    e()  # OK

    e = LocalCatalogEntry('', '', driver, args={'arg1': "1"},
                          parameters=[up], getenv=False)
    s = e()  # OK
    assert s.kwargs['arg1'] == 1  # a number, not str


def test_overrides():
    e = LocalCatalogEntry('', '', driver, args={'arg1': "oi"})
    s = e(arg1='hi')
    assert s.kwargs['arg1'] == 'hi'

    e = LocalCatalogEntry('', '', driver, args={'arg1': "{{name}}"})
    s = e(name='hi')
    assert s.kwargs['arg1'] == 'hi'

    os.environ['INTAKE_TEST_VAR'] = 'another'
    e = LocalCatalogEntry('', '', driver, args={'arg1': "oi"})
    s = e(arg1='{{env(INTAKE_TEST_VAR)}}')
    assert s.kwargs['arg1'] == 'another'

    up = UserParameter('arg1', type='int')
    e = LocalCatalogEntry('', '', driver, args={'arg1': 1},
                          parameters=[up])
    with pytest.raises(ValueError):
        e(arg1='oi')

    s = e(arg1='1')
    assert s.kwargs['arg1'] == 1
