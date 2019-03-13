from functools import wraps
import arrow
from datadog import statsd
from flask import current_app, request
import jwt
from werkzeug.exceptions import Unauthorized
from werkzeug.local import LocalProxy
from pd.ext import sentry
from pd.facebook.models import User
from pd.facebook.schema import UserSchema


def _get_current_user():
    if not hasattr(request, 'current_user'):
        try:
            uid = request.current_user_data['id']
        except AttributeError:
            request.current_user = None
        else:
            request.current_user = User.query.get(uid)
    return request.current_user


current_user = LocalProxy(_get_current_user)
current_user_data = LocalProxy(
    lambda: getattr(request, 'current_user_data', None))


def _extract_token():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise Unauthorized('Authorization header is expected')
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise Unauthorized('Authorization header must start with "Bearer"')
    if len(parts) == 1:
        raise Unauthorized('Token not found in Authorization header')
    if len(parts) > 2:
        raise Unauthorized(
            'Authorization header must be in the format: Bearer\s{token}')
    return parts[1]


def _decode_token(token, secret, **kwargs):
    try:
        payload = jwt.decode(token, secret, **kwargs)
    except jwt.ExpiredSignatureError as e:
        raise Unauthorized('token is expired')
    except jwt.DecodeError as e:
        raise Unauthorized('token signature is invalid')
    return payload


def _get_token():
    token = _extract_token()
    request.current_user_data = _decode_token(
        token, current_app.config['SECRET_KEY'],
        leeway=current_app.config['JWT_LEEWAY'],
    )
    statsd.set('auth.users.unique', request.current_user_data['id'])


def auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            _get_token()
        except Unauthorized as e:
            statsd.increment('auth.error')
            current_app.logger.info('Authentication error: %s', e)
            raise
        sentry.user_context(current_user_data)
        return func(*args, **kwargs)

    wrapped._auth_required = True

    return wrapped


def auth_optional(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            _get_token()
        except Unauthorized:
            pass
        return func(*args, **kwargs)

    wrapped._auth_optional = True

    return wrapped


def _create_token(payload, secret, ttl=7200):
    now = arrow.utcnow()
    payload.update({
        'iat': now.timestamp,
        'exp': now.replace(seconds=ttl).timestamp,
    })
    return jwt.encode(payload, secret).decode()


_user_schema = UserSchema()


def create_token(user):
    return _create_token(
        _user_schema.dump(user).data,
        ttl=current_app.config['JWT_TTL'],
        secret=current_app.config['SECRET_KEY'],
    )
