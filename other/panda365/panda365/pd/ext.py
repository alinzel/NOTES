from functools import partial, wraps
from facebook import GraphAPI
from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_mail import Mail
from pd.admin.base import AdminIndexView
from pd.payment.payssion import Extension as Payssion
from pd.s3 import S3StorageExtension
from raven.contrib.flask import Sentry
from requests import Session
import logging


# some APIs require the access token to be set at GraphAPI creation time
# use this factory to ensure that we're still reusing the underlying
# requests session.
_graph_session = Session()
graph_factory = partial(GraphAPI, session=_graph_session)

admin = Admin(
    name='Panda 365',
    index_view=AdminIndexView(),
    template_mode='bootstrap3',
)
mail = Mail()
s3ext = S3StorageExtension()
sentry = Sentry(logging=True, level=logging.ERROR)
payssion = Payssion()

# rate limit
limiter = Limiter(
    key_func=get_ipaddr, headers_enabled=True, auto_check=False)


def limit_and_check(
    limit_value, key_func=None, per_method=True, methods=None,
    error_message=None, exempt_when=None,
):

    def inner(func):
        limiter.limit(
            limit_value, key_func=key_func, per_method=per_method,
            methods=None, error_message=None, exempt_when=exempt_when,
        )(func)

        @wraps(func)
        def check(*args, **kwargs):
            limiter.check()
            return func(*args, **kwargs)

        return check

    return inner


limiter.limit_and_check = limit_and_check
