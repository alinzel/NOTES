from contextlib import contextmanager
import logging
import re
import sys

import arrow
from flask import current_app, request
from flask_babelex import get_locale
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import MetaData, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import ArrowType, TranslationHybrid
from sqlalchemy_utils.listeners import force_instant_defaults
from werkzeug.local import LocalProxy


logger = logging.getLogger('panda.db')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


# def _default(val):
#     if isinstance(val, arrow.Arrow):
#         return val.isoformat()
#     if isinstance(val, Enum):
#         return val.value
#     raise TypeError('cannot encode type "{}" - "{}"'.format(type(val), val))


# def pg_json_serializer(d):
#     return json.dumps(d, default=_default)


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
# db = SQLAlchemy(metadata=metadata, session_options={
#     'json_serializer': pg_json_serializer,
# })
db = SQLAlchemy(metadata=metadata, session_options={'expire_on_commit': False})
# listeners
force_instant_defaults()
BaseModel = db.Model


class Query(BaseQuery):

    def paginate(self, page=None, per_page=None, err_out=False):
        if not per_page:
            if request:
                try:
                    per_page = int(request.args.get('per_page'))
                except (TypeError, ValueError):
                    pass
            if not per_page:  # no request or per_page not set in request.args
                per_page = current_app.config['API_PER_PAGE']

        return super().paginate(page, per_page, err_out)

    def get_or_404_json(self, ident):
        from pd.api import abort_json
        object = self.get(ident)
        if object is None:
            abort_json(404, message='{} {} not found'.format(
                self._entities[0].type.__tablename__, ident
            ))
        return object


class Model(BaseModel):
    __abstract__ = True
    query_class = Query

    id = db.Column(db.Integer, primary_key=True)


class CreateTimestampMixin:
    created_at = db.Column(ArrowType, default=arrow.utcnow)


class TimestampMixin(CreateTimestampMixin):
    updated_at = db.Column(ArrowType, default=arrow.utcnow)


@event.listens_for(TimestampMixin, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated_at = arrow.utcnow()


db.Model = Model
# lazy session is used to postpone the creation of sessions. It is intended to
# be used in tests, so that `db_session` fixture can have a chance to hijack
# the transactions
lazy_session = LocalProxy(lambda: db.session)


@contextmanager
def ignore_integrity_error(err_pattern):
    try:
        yield
    except IntegrityError as e:
        match = re.findall(err_pattern, e.args[0].replace('\n', '.'))
        if match:
            logger.debug('ignored integrity error: %s', e)
            db.session.rollback()
        else:  # pragma: no cover
            raise


# internationalization


def _get_locale():
    l = get_locale()
    if l:
        if l.territory:
            return '{}_{}'.format(l.language, l.territory).lower()
        return l.language


translation_hybrid = TranslationHybrid(
    current_locale=_get_locale,
    default_locale='en',
)


__all__ = [
    'db',
    'lazy_session',
    'Model',
    'ignore_integrity_error',
    'translation_hybrid',
]
