from marshmallow import Schema as _BaseSchema, post_dump
from marshmallow_sqlalchemy import (
    ModelSchema as _BaseModelSchema, ModelConverter
)
from sqlalchemy_utils import CurrencyType
from .fields import Currency


ModelConverter.SQLA_TYPE_MAPPING.update({
    CurrencyType: Currency,
})


class Schema(_BaseSchema):

    class Meta:
        ordered = True
        strict = True


class ModelSchema(_BaseModelSchema):

    class Meta:
        ordered = True
        strict = True

    @post_dump
    def add_type(self, data):
        data['_type'] = self.Meta.model.__tablename__
