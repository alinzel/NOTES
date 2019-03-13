from decimal import Decimal

import pytest

from pd.test_utils import (
    assert_dict_like, assert_sorted_by, Any, AnyDateString,
)


@pytest.mark.parametrize('value', [
    1,
    'string',
    1.2,
    Decimal('1.2'),
    {},
    [],
])
def test_any(value):
    assert Any() == value


def test_any_of_type():
    assert Any(int) == 1
    assert Any(int) != 1.0


@pytest.mark.parametrize('fmt,value,does_equal', [
    ['%Y', '2014', True],
    ['%Y', '2014-04', False],
    ['%Y', 2014, False],  # not a string
    ['%Y-%m-%d %H:%M:%S.%f', '2014-05-15 12:17:00.000', True],
])
def test_any_date_str(fmt, value, does_equal):
    assert (AnyDateString(fmt) == value) == does_equal


def test_dict_like():
    me = {
        'a': 1,
        'b': 2,
        'c': {
            'aa': 'e',
            'bb': 'f',
        },
        'd': {},
    }
    # part of simple keys
    assert_dict_like(me, {
        'a': 1,
    })
    # part of nested dict keys
    assert_dict_like(me, {
        'c': {
            'aa': 'e',
        }
    })
    # non-exist key
    with pytest.raises(AssertionError) as exc_info:
        assert_dict_like(me, {
            'e': 123
        })
    exc_info.match('key ".e" does not exist')
    # non-exist nested key
    with pytest.raises(AssertionError) as exc_info:
        assert_dict_like(me, {
            'c':  {
                'cc': 123,
            }
        })
    exc_info.match('key ".c.cc" does not exist')
    # nested key not equal
    with pytest.raises(AssertionError) as exc_info:
        assert_dict_like(me, {
            'c':  {
                'aa': 2,
            }
        })
    assert exc_info.match('key ".c.aa" does not equal: \'e\' != 2')
    # not a dict
    for v in (
        ['123'],
        {'c': None},
    ):
        with pytest.raises(AssertionError) as exc_info:
            assert_dict_like(me, {
                'c': None,
            })
        exc_info.match('does not equal: None is not dict-like')


def test_sorted_by():
    items = [{
        'id': i,
        'weight': -i,
    } for i in range(10)]
    assert_sorted_by(items, lambda item: item['id'])
    assert_sorted_by(items, lambda item: -item['weight'])
    assert_sorted_by(items, 'id')
    assert_sorted_by(items, '-weight')
