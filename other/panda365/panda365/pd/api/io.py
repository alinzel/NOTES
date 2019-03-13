from collections import Mapping
from inspect import signature as get_signature, Signature
from functools import wraps
from flask import jsonify, current_app
from flask_sqlalchemy import Pagination
from marshmallow import fields, Schema
from marshmallow.exceptions import ValidationError
from webargs.core import argmap2schema
from webargs.flaskparser import use_kwargs
from pd.sqla import db


class PageInfoSchema(Schema):
    pages = fields.Int(dump_to='total_pages')
    page = fields.Int()
    next_num = fields.Int(dump_to='next_page')
    prev_num = fields.Int(dump_to='prev_page')
    total = fields.Int(dump_to='total_items')


_page_info_schema = PageInfoSchema(strict=True)


class SerializationError(Exception):

    def __init__(self, messages, error):
        self.messages = messages
        self.error = error


class ProgrammingError(Exception):
    pass


def get_input_schema(sig):
    decorated = [
        p.annotation is not Signature.empty for p in sig.parameters.values()]
    if any(decorated):
        if len(decorated) == 1:
            name, parameter = [item for item in sig.parameters.items()][0]
            if isinstance(parameter.annotation, Schema):
                if parameter.kind != parameter.VAR_KEYWORD:
                    raise ProgrammingError(
                        '"{name}" must be a kwargs when using a schema. '
                        'Change it to "**{name}"'.format(name=name)
                    )
                parameter.annotation.strict = True
                return parameter.annotation
        return {name: p.annotation for name, p in sig.parameters.items()}


def get_output_schema(sig):
    out_schema = sig.return_annotation

    if out_schema is Signature.empty:
        out_schema = None
    else:
        if isinstance(out_schema, Schema):
            out_schema.strict = True
        elif isinstance(out_schema, Mapping):
            for name, field in out_schema.items():
                if not isinstance(field, fields.Field):
                    raise ProgrammingError(
                        'value of "{}" must be an instance of marshmallow.'
                        'Field'.format(name))
            out_schema = argmap2schema(out_schema)()
        else:
            raise ProgrammingError(
                'return annotation must be an instance of '
                'marshmallow.Schema or a mapping of marshmallow.Field'
            )
    return out_schema


def serialize(value, schema):
    if schema.many:
        if isinstance(value, db.Model.query_class):
            value = value.paginate()
        if isinstance(value, Pagination):
            page_info = _page_info_schema.dump(value).data
            value = value.items
        else:
            page_info = None
    try:
        data = schema.dump(value).data
    except ValidationError as e:
        raise SerializationError(e.messages, error=e)

    if schema.many:
        return dict(objects=data, page_info=page_info)
    return data


def io_annotated(f):
    sig = get_signature(f)
    # input schema
    input_schema = get_input_schema(sig)
    if input_schema:
        f = use_kwargs(input_schema)(f)
    # output schema
    output_schema = get_output_schema(sig)

    @wraps(f)
    def inner(*args, **kwargs):
        ret = f(*args, **kwargs)
        # short-circuit on response objects
        if isinstance(ret, current_app.response_class):
            return ret
        if output_schema:
            return jsonify(serialize(ret, output_schema))
        return ret

    inner._input_schema = input_schema
    inner._output_schema = output_schema

    return inner
