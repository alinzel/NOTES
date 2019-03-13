from unittest.mock import patch, MagicMock
from flask import _request_ctx_stack
from pd.sqla import Query
# from enum import Enum
# import arrow
# import pytest

# from pd.sqla import _default, pg_json_serializer


# class Foo:
#     pass


# def test_json_default():
#     with pytest.raises(TypeError):
#         _default(Foo())


# class Color(Enum):
#     red = 'red'
#     blue = 'blue'


# @pytest.mark.parametrize('value,expected', [
#     [arrow.get('2017-01-01'), '"2017-01-01T00:00:00+00:00"'],
#     [Color.red, '"red"'],
# ])
# def test_json_serializer(value, expected):
#     assert pg_json_serializer(value) == expected


def test_default_per_page(app, config, monkeypatch):
    monkeypatch.setitem(config, 'API_PER_PAGE', 11)
    q = Query(MagicMock())
    # pytest flask automatically pushes a request context;
    # here we temporarily disable it
    tmp = _request_ctx_stack.top
    tmp.pop()
    with patch('pd.sqla.BaseQuery.paginate') as mock:
        def _assert_per_page(expected):
            assert mock.call_args[0][1] == expected
        # no request
        with app.app_context():
            q.paginate()
            _assert_per_page(11)
            q.paginate(per_page=10)
            _assert_per_page(10)
        # in a request
        with app.test_request_context('/'):
            # no per_page arg
            q.paginate()
            _assert_per_page(11)

        with app.test_request_context('/?per_page=10'):
            q.paginate()
            _assert_per_page(10)

            q.paginate(per_page=100)
            _assert_per_page(100)
    tmp.push()
