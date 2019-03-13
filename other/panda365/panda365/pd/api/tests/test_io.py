import json
from flask import jsonify, request, Flask
from flask_sqlalchemy import Pagination
from marshmallow import fields, Schema, post_dump, ValidationError
import pytest
from pd.test_utils import Client
from ..io import io_annotated, ProgrammingError, SerializationError
from .. import handle_serialization_error


pytestmark = pytest.mark.usefixtures('app_context')


@pytest.fixture
def app():
    a = Flask(__name__)
    a.testing = True
    a.test_client_class = Client
    a.register_error_handler(SerializationError, handle_serialization_error)
    return a


@pytest.fixture
def client(app):
    return app.test_client()


class FooSchema(Schema):
    a = fields.Int()
    b = fields.Str()

    @post_dump
    def validate_a(self, data):
        if data.get('a', 0) > 10:
            raise ValidationError('a cannot be greater than 10')


@pytest.mark.parametrize('annotation', [
    FooSchema(),
    {'a': fields.Int(), 'b': fields.Str()}
])
def test_output_item(app, client, annotation):

    @app.route('/', methods=['POST'])
    @io_annotated
    def echo_view() -> annotation:
        return request.form

    resp = client.post('/', data={
        'a': 10,
        'b': 'str',
        'c': 10,
    })
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    assert json.loads(resp.data) == {
        'a': 10,
        'b': 'str',
    }


def test_output_serialization_error(app, client):
    @app.route('/', methods=['POST'])
    @io_annotated
    def echo_view() -> FooSchema():
        return request.form

    resp = client.post('/', data={'a': 1111})
    assert resp.status_code == 500
    assert 'greater than 10' in str(resp.json['errors']['_schema'])


@pytest.mark.parametrize('paginated', [True, False])
def test_output_items_with_schema(app, client, paginated):

    items = [{'a': 10, 'b': 'b'}] * 2

    @app.route('/')
    @io_annotated
    def view() -> FooSchema(many=True):
        if paginated:
            return Pagination(None, 1, 10, 21, items)
        return items

    # if an iterable is returned, no page_info is returned
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json['objects'] == items
    if paginated:
        assert resp.json['page_info'] == {
            'total_pages': 3,
            'page': 1,
            'next_page': 2,
            'prev_page': None,
            'total_items': 21,
        }
    else:
        assert not resp.json['page_info']


def test_output_items_without_annotation(app, client):
    """
    if no return annotation is provided, the result should be returned as is
    """
    @app.route('/')
    @io_annotated
    def echo_view():
        return '123'

    resp = client.get('/')
    assert resp.data == b'123'


def test_output_response_obj(app, client):
    """
    if a response object is returned, output schema should be skipped
    """
    @app.route('/')
    @io_annotated
    def echo_view() -> FooSchema():
        resp = jsonify(error='bad request')
        resp.status_code = 400
        return resp

    resp = client.get('/')
    assert resp.status_code == 400
    assert resp.json == {'error': 'bad request'}


@pytest.mark.parametrize('annotation,expected_err', [
    [int, 'must be an instance of marshmallow.Schema'],
    [{'a': int}, 'must be an instance of marshmallow.Field'],
])
def test_output_annotation_error(app, annotation, expected_err):

    with pytest.raises(ProgrammingError) as exc_info:
        @app.route('/')
        @io_annotated
        def echo_view() -> annotation:
            return '1'  # pragma: no cover

    exc_info.match(expected_err)


def test_input_schema(app, client):

    @app.route('/', methods=['POST'])
    @io_annotated
    def echo_view(what: fields.Int()) -> {'what': fields.Int()}:
        return dict(what=what)

    resp = client.post('/', json={'what': 'sdf'})
    assert resp.status_code == 422

    resp = client.post('/', json={'what': 1})
    assert resp.status_code == 200
    assert resp.json['what'] == 1, resp.json


def test_input_schema_locations(app, client):
    @app.route('/', methods=['POST'])
    @io_annotated
    def add_view(
            a: fields.Int(location='query'), b: fields.Int(location='form')
    ) -> {'result': fields.Int()}:
        return dict(result=a + b)

    resp = client.post('/', query_string={'a': 2}, data={'b': 1})
    assert resp.json['result'] == 3


def test_input_schema_missing_data(app, client):
    @app.route('/', methods=['POST'])
    @io_annotated
    def view(a: fields.Int(location='query')):
        return str(a)

    resp = client.post('/')
    assert b'missing' in resp.data


def test_input_schema_cls(app):

    class InputSchema(Schema):
        a = fields.Int()
        b = fields.Int()

    with pytest.raises(ProgrammingError):
        # when using a schema as annotation, the argument must be a kwargs
        @io_annotated
        def error_view(kwargs: InputSchema()):
            pass  # pragma: no cover

    @io_annotated
    def add_view(**kwargs: InputSchema()):
        return kwargs['a'] + kwargs['b']

    with app.test_request_context(
        '/',
        data=json.dumps({'a': 1, 'b': 2}),
        method='POST',
        content_type='application/json'
    ):
        assert add_view() == 3


def test_handle_serialization_error(app, monkeypatch):
    resp = handle_serialization_error(SerializationError('test', None))
    assert resp.status_code == 500
    assert 'Serialization Error' in resp.json['message']
