from base64 import b64decode
from io import BytesIO
from marshmallow import fields, validate, ValidationError
from sqlalchemy import inspect
from werkzeug.datastructures import FileStorage
import binascii
import uuid


class DataURL(fields.String):
    """
    data url as defined in RFC 2397:

        data:[mimetype][;base64],[data]

    Usually used only for parsing incoming data.
    """
    default_error_messages = {
        'malformed': 'cannot be parsed as a data url.',
        'padding': 'payload is incorrectly padded',
        'mimetype': 'mimetype not allowed',
    }

    def __init__(self, *args, allowed_mimetypes=None, **kwargs):
        if kwargs.get('load_only') is False:
            raise ValueError('this field can only be used to load data; '
                             'however load_only is set to False')
        kwargs['load_only'] = True
        kwargs.setdefault('description',
                          'RFC 2397 data url. '
                          'Format: `data:[mimetype][;base64],[data]`')
        super().__init__(*args, **kwargs)
        if allowed_mimetypes:
            self._allowed_mimetypes = set(allowed_mimetypes)
        else:
            self._allowed_mimetypes = None

    def validate_mimetype(self, mimetype):
        if self._allowed_mimetypes and mimetype not in self._allowed_mimetypes:
            self.fail('mimetype')

    def _deserialize(self, value, attr, obj):
        value = super()._deserialize(value, attr, obj)
        if not value.startswith('data:'):
            self.fail('malformed')
        try:
            comma_index = value.index(',')
        except ValueError:
            self.fail('malformed')
        # 5 is for "data:"
        mimetype, _ = value[5:comma_index].split(';')
        if not mimetype:
            self.fail('malformed')
        self.validate_mimetype(mimetype)
        # construct stream from data
        try:
            # +1 to skip the comma
            data = b64decode(value[comma_index + 1:])
        except binascii.Error:
            self.fail('padding')
        name = '{}.{}'.format(uuid.uuid4().hex, mimetype.split('/')[-1])
        return FileStorage(
            stream=BytesIO(data),
            content_type=mimetype,
            filename=name,
            name=name,
        )


class Currency(fields.String):

    def _deserialize(self, value, attr, obj):
        raise NotImplementedError()  # pragma: no cover

    def _serialize(self, value, attr, obj):
        if value:  # pragma: no cover
            return {
                'code': value.code,
                'symbol': value.symbol
            }


class Enum(fields.String):

    def __init__(self, enum, choices=None, *args, **kwargs):
        """
        :param enum: enum used to validate incoming value
        :param list choices:
            by default all items of the enum are used. If only a subset of the
            enum should be used, pass them in here.

        Example::

            class Status(Enum):
                ok = 1
                fail = 2
                my_dirty_internal_enum_which_should_not_be_told = 3

            class FooSchema(Schema):
                status = Enum(
                    enum=Status, choices=[Status.ok, Status.fail])
        """
        self._enum = enum
        validators = kwargs.setdefault('validate', [])
        validators.append(validate.OneOf(choices=choices or enum))
        self.default_error_messages.update(
            dict(bad_enum='{value} is not a valid choice'))
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value:
            return getattr(value, 'name')

    def _deserialize(self, value, attr, obj):
        value = super()._deserialize(value, attr, obj)
        try:
            return getattr(self._enum, value)
        except AttributeError:
            self.fail('bad_enum', value=repr(value))


class ProductInfo(fields.String):

    def __init__(self, **kwargs):
        kwargs.setdefault(
            'description', '''
a list of objects, each has the key `name` and
`value`. Example:

        [
            {
                "name": "Brand",
                "value": "Apple"
            }, {
                "name": "Country",
                "value": "China"
            }
        ]
            '''
        )
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj):
        if not value:
            return
        ret = []
        for line in value.split('\n'):
            k, v = line.split(':')
            ret.append(dict(name=k, value=v))
        return ret

    def _deserialize(self, value, attr, obj):
        raise NotImplementedError()  # pragma: no cover


class ModelPKField(fields.Integer):
    """A field representing a model instance.

    This serializes the value to the id of the model, and deserialize from
    a given id to a model instance

    :param model_class: a db Model
    :param filters: filters to apply when getting the record from id

    """
    default_error_messages = {
        'notfound': 'record cannot be found',
    }

    def __init__(self, model_class, *filters, **kwargs):
        pks = inspect(model_class).primary_key
        if len(pks) > 1:  # pragma: no cover
            raise ValueError('only support models with 1 primary key')
        self.model = model_class
        self.filters = filters
        self.pk_name = pks[0].name
        super().__init__(**kwargs)

    # def _serialize(self, value, attr, obj):
    #     if isinstance(value, self.model):
    #         return getattr(value, self.pk_name)

    def _deserialize(self, value, attr, obj):
        value = super()._deserialize(value, attr, obj)
        filters = []
        for f in self.filters:
            if callable(f):
                f = f()
            filters.append(f)
        obj = self.model.query.filter(
            getattr(self.model, self.pk_name) == value,
            *filters
        ).first()
        if not obj:
            raise ValidationError('{} {} cannot be found'.format(
                self.model.__name__, value,
            ))
        return obj
