"""
This module contains utilities for comparing staff. Use them to make asserts
easier.
"""
from contextlib import contextmanager
import arrow
from bs4 import BeautifulSoup
from flask import Response as BaseResponse
from flask import url_for
from flask.json import dumps as json_dumps
from flask.testing import FlaskClient as BaseClient
from werkzeug.utils import cached_property
from werkzeug.datastructures import MultiDict


class Any:

    def __init__(self, type=None):
        self.type = type

    def __eq__(self, other):
        return True if not self.type else isinstance(other, self.type)

    def __repr__(self):
        return 'Any({})'.format(self.type)


class AnyDateString(Any):

    def __init__(self, fmt):
        '''
        :param str fmt:
        '''
        self.fmt = fmt
        super().__init__(str)

    def __eq__(self, other):
        if super().__eq__(other):
            try:
                arrow.Arrow.strptime(other, self.fmt)
            except ValueError:
                return False
            else:
                return True
        return False

    def __repr__(self):
        return 'AnyDateString({})'.format(self.fmt)


def _assert_dict_like(me, other, parent_key=''):

    for k in other:
        try:
            my_value = me[k]
        except KeyError:
            raise AssertionError(
                'key "{}.{}" does not exist'.format(parent_key, k))
        try:
            if isinstance(my_value, dict):
                _assert_dict_like(
                    my_value, other[k], '{}.{}'.format(parent_key, k))
            else:
                assert other[k] == my_value, \
                    'key "{}.{}" does not equal: {} != {}'.format(
                        parent_key, k, repr(my_value), repr(other[k]))
        except TypeError:
            raise AssertionError(
                'key "{}.{}" does not equal: {} is not dict-like'.format(
                    parent_key, k, other[k])
            )


def assert_dict_like(me, other):
    _assert_dict_like(me, other)


def assert_sorted_by(items, key, reverse=False):
    """
    check if the given list is ordered by key.

    :param list items: list to be checked
    :param key:
        a function which is used to get the order by attribute from the items
    """
    if isinstance(key, str):
        if key[0] == '-':
            reverse = True
            _key = key[1:]
        else:
            _key = key

        def key(item): return item[_key]
    assert sorted(items, key=key, reverse=reverse) == items


# test client
class Response(BaseResponse):

    @cached_property
    def text(self):
        return self.data.decode()

    @cached_property
    def soup(self):
        return BeautifulSoup(self.text, 'html.parser')


class Client(BaseClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.token = None

    def login(self, user):
        from pd.auth.jwt import create_token
        self.user = user
        self.token = create_token(user)

    def logout(self):
        self.user = self.token = None

    @contextmanager
    def auth_context(self, user):
        old_user = self.user
        self.login(user)
        yield self
        self.login(old_user)

    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            assert 'data' not in kwargs, \
                'cannot set data and json at the same time'
            kwargs['data'] = json_dumps(kwargs.pop('json'))
            headers = kwargs.setdefault('headers', {})
            headers['content-type'] = 'application/json'
        # auth
        if self.user:
            headers = kwargs.setdefault('headers', {})
            if 'Authorization' not in headers:
                headers['Authorization'] = 'Bearer {}'.format(self.token)
        return super().open(*args, **kwargs)


class AdminPage:

    def __init__(self, soup):
        self.soup = soup

    def get_messages_by(self, category):
        return [div.text.strip()
                for div in self.soup.select('.alert-{}'.format(category))]


class ModelListPage(AdminPage):
    pass


class AdminClient(BaseClient):

    @property
    def user_id(self):
        with self.session_transaction() as sess:
            if 'user_id' in sess:
                return int(sess['user_id'])

    def login(self, email, password):
        self.post('/admin/auth/login', data={
            'email': email,
            'password': password,
        })
        return bool(self.user_id)

    def logout(self):
        self.get('/admin/auth/logout')

    def action(self, model, action, *rowids):
        data = [('action', action)]
        for rid in rowids:
            data.append(('rowid', rid))
        resp = self.post(
            url_for('{}.action_view'.format(model)),
            data=MultiDict(data), follow_redirects=True,
        )
        resp.page = ModelListPage(resp.soup)
        return resp
