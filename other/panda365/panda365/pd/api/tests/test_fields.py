from enum import Enum
from flask import request
from marshmallow import Schema
from pd.api.fields import DataURL, Enum as EnumField, ProductInfo, ModelPKField
from pd.groupon.factory import Batch, BatchFactory, CategoryFactory
import pytest


def test_data_url_field(png_data_url, png_path):
    class FooSchema(Schema):
        image = DataURL()

    schema = FooSchema()
    result = schema.load({
        'image': png_data_url
    })
    assert not result.errors
    file_storage = result.data['image']
    assert file_storage.mimetype == 'image/png'
    with open(png_path, 'rb') as f:
        assert f.read() == file_storage.stream.read()


@pytest.mark.parametrize('data,expected_error', [
    [{}, 'mimetype not allowed'],
    [{'image': 'blah'}, 'cannot be parsed'],
    [{'image': 'data:blah'}, 'cannot be parsed'],
    [{'image': 'data:;base64,asdfadf'}, 'cannot be parsed'],
    [{'image': 'data:image/jpeg;base64,/9j'}, 'payload is incorrectly padded']
])
def test_data_url_mimetype_errors(png_data_url, data, expected_error):
    class FooSchema(Schema):
        image = DataURL(allowed_mimetypes=['image/jpeg'])

    schema = FooSchema()
    result = schema.load(dict({
        'image': png_data_url
    }, **data))
    assert expected_error in result.errors['image'][0]


def test_data_url_load_only():
    with pytest.raises(ValueError):
        class FooSchema(Schema):
            image = DataURL(load_only=False)


def test_enum():
    class Status(Enum):
        ok = 1
        fail = 2

    class Foo:

        def __init__(self, status):
            self.status = status

    class FooSchema(Schema):
        status = EnumField(enum=Status)

    # dumps
    schema = FooSchema()
    foo = Foo(status=Status.ok)
    dumped = schema.dump(foo).data
    # dumped status should be name of the enum, lower cased
    assert dumped == {
        'status': 'ok'
    }
    foo.status = None
    assert schema.dump(foo).data['status'] is None
    # loads
    loaded = schema.load(dumped).data
    assert loaded['status'] == Status.ok
    # load errors
    result = schema.load(dict(status='what'))
    assert result.errors['status'] == ["'what' is not a valid choice"]

    # accepted value should be in choices
    class FooSchema(Schema):
        status = EnumField(enum=Status, choices=[Status.ok])

    schema = FooSchema()
    # loads
    # should raise validation error for fail, since it's not allowed in choices
    loaded = schema.load(dict(status='fail'))
    assert 'status' in loaded.errors
    # ok is fine since it's in choices
    loaded = schema.load(dict(status='ok'))
    assert not loaded.errors


def test_product_info():
    class FooSchema(Schema):
        info = ProductInfo()

    foo = {'info': 'a:b\nc:d'}
    schema = FooSchema()
    assert schema.dump(foo).data == {
        'info': [{
            'name': 'a',
            'value': 'b',
        }, {
            'name': 'c',
            'value': 'd',
        }]
    }

    assert schema.dump({'info': None}).data == {
        'info': None
    }


@pytest.mark.db
def test_model_pk_field(app):
    CategoryFactory()
    batch = BatchFactory()

    class FooSchema(Schema):
        batch = ModelPKField(Batch, load_from='id', dump_to='id')

    # load
    schema = FooSchema()
    result = schema.load(data=dict(id=batch.id))
    assert result.data['batch'] is batch

    class FooSchema(Schema):
        product = ModelPKField(
            Batch,
            # filters
            Batch.sold_num >= 1,  # can be a simple filter
            # can also be a callable; useful if it needs to access request
            lambda: Batch.currency == request.args['currency'],
            load_from='id',
        )

    schema = FooSchema()
    with app.test_request_context('/?currency=USD'):
        result = schema.load(data=dict(id=batch.id))
    assert result.errors
    assert 'cannot be found' in result.errors['id'][0]
