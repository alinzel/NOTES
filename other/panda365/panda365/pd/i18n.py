from flask import current_app, request
from flask_babelex import Babel, Domain
from sqlalchemy_utils import i18n


babel = Babel(default_domain=Domain(domain='messages'))


def _get_locale():
    default = current_app.config['BABEL_DEFAULT_LOCALE']
    if request.path.startswith('/admin'):
        if request.accept_languages.best:
            return request.accept_languages.best
        else:
            return default
    return request.accept_languages.best_match(
        current_app.config['BABEL_SUPPORTED_LOCALES'],
        default=default,
    )


@babel.localeselector
def get_locale():
    # in flask-babelex, the load_locale call which converts locale code
    # to locale object, expects the seperator to be "_". Some browsers
    # like chrome uses "-" as sep.
    return _get_locale().replace('-', '_')


@babel.timezoneselector
def get_timezone():
    if request.path.startswith('/admin'):
        return current_app.config['ADMIN_TIMEZONE']


i18n.get_locale = get_locale
