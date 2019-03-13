import logging
from marshmallow import ValidationError
import mimetypes
from flask import Flask, make_response, request, json
from flask_cors import CORS
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.contrib.fixers import ProxyFix
from . import commands
from .admin.auth import ConfirmRegisterForm
from .admin.models import AdminRole, AdminUser
from .api import (
    handle_422, handle_serialization_error, SerializationError, JSONEncoder,
    handle_marshmallow_validation_error,
)
from .config import load_config
from .i18n import babel
from .sqla import db, lazy_session
from .ext import admin, mail, s3ext, sentry, payssion, limiter
from .statsd import install_hooks
from .tasks import celery_app, configure_celery

mimetypes.init()


def create_app(config_name=None, **kwargs):
    app = Flask('pd')

    load_config(app, config_name, **kwargs)

    if app.config['NUM_PROXIES'] > 0:  # pragma: no cover
        app.wsgi_app = ProxyFix(app.wsgi_app, app.config['NUM_PROXIES'])

    if not app.debug and not app.testing:  # pragma: no cover
        prod_handler = app.logger.handlers[-1]
        prod_handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.propagate = True

    # extensions
    db.init_app(app)
    # sentry
    sentry.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = app.config[
        'BABEL_DEFAULT_LOCALE'].replace('-', '_')
    app.config['BABEL_SUPPORTED_LOCALES'] = [
        l.replace('-', '_') for l in app.config['BABEL_SUPPORTED_LOCALES']]
    babel.init_app(app)
    Migrate(app, db)
    mail.init_app(app)
    admin.init_app(app)
    s3ext.init_app(app)
    Security(
        app,
        SQLAlchemyUserDatastore(db, AdminUser, AdminRole),
        confirm_register_form=ConfirmRegisterForm,
    )
    CORS(app, resources=r'/v1/*')
    commands.init_app(app)
    limiter.init_app(app)
    install_hooks(app)
    # payment
    payssion.init_app(app)
    if app.debug:  # pragma: no cover
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    if app.config['DOCS_ENABLE_TEST_CLIENT']:  # pragma: no cover
        # show debug toolbar for API responses
        @app.after_request
        def as_html(resp):
            if request.path.startswith('/v1') \
                    and 'html' in request.headers['accept']:
                if request.is_xhr:
                    data = resp.get_data().decode()
                    # the test api client uses ajax
                    # flask does not beautify ajax response by default
                    # here we beautify it
                    if resp.content_type == 'application/json':
                        data = json.dumps(
                            json.loads(data), indent=4, sort_keys=True)
                    resp = make_response(
                        '<html><body><pre>{}</pre></body></html>'.format(
                            data))
            return resp

    # api
    app.json_encoder = JSONEncoder
    app.register_error_handler(422, handle_422)
    app.register_error_handler(
        ValidationError, handle_marshmallow_validation_error)
    app.register_error_handler(SerializationError, handle_serialization_error)

    # routes

    # payments
    from .payment.base import configure_payments
    configure_payments(app)
    # FIXME: turn back on strict slashes
    app.url_map.strict_slashes = False
    from .facebook.views import facebook
    from .facebook.api import api as fb_api
    from .api.api import api
    from .auth.api import auth
    from .conf.api import api as conf_api
    from .bookmark.api import api as bookmark_api
    from .wish.api import api as wish_api
    from .wish.views import bp as wish_bp
    from .groupon.api import api as groupon_api
    from .views import bp as www_bp
    from .groupon.views import share
    from .guest.view import reply
    for bp in (
            facebook, api, auth, fb_api, conf_api, bookmark_api, wish_api,
            wish_bp, groupon_api, www_bp, share, reply
    ):
        app.register_blueprint(bp)

    # admin
    from .admin.admin import AdminRoleAdmin, AdminUserAdmin
    from .conf.admin import ConfAdmin
    from .facebook.admin import (
        CommentAdmin, LikeAdmin, PostAdmin, ReplyAdmin, PostPhotoAdmin,
        PreSaleProductAdmin, AllPostAdmin, OnSaleProductAdmin,
        WishCommentAdmin, ProductCommentAdmin,
    )
    from .conf.models import Conf
    from .groupon.models import (
        Product, Batch, Game, Order, Category, Spec, BatchSpec, SpecOption)
    from .groupon.admin import (
        ProductAdmin, BatchAdmin, GameAdmin, OrderAdmin, CategoryAdmin,
        SpecAdmin, BatchSpecAdmin, SpecOptionAdmin)
    from .facebook.models import Comment, Like, Post, PostPhoto, Country
    from .vendor.admin import VendorAdmin
    from .vendor.models import Vendor
    from .wish.admin import WishAdmin, TipAdmin, VoteAdmin
    from .wish.models import Wish, Tip, Vote
    from .payment.admin import PaymentDevAdmin, PaymentAdmin
    from .payment.models import Payment

    admin_model_view_args = [
        (PostAdmin, Post, dict(
            name='普通Post', endpoint='normal-post')),
    ]
    for country in Country:
        admin_model_view_args.append(
            (PreSaleProductAdmin, Post, dict(
                category='{}商品'.format(country.admin_label),
                name='预售商品',
                endpoint='presale_post_{}'.format(country.name),
                country=country,
            ))
        )
        admin_model_view_args.append(
            (OnSaleProductAdmin, Post, dict(
                category='{}商品'.format(country.admin_label),
                name='在售商品',
                endpoint='onsale_post_{}'.format(country.name),
                country=country,
            ))
        )
    admin_model_view_args += [
        (ReplyAdmin, Comment, dict(
            category='Dev', name='Reply', endpoint='reply')),
        (CommentAdmin, Comment, dict(
            category='Dev', name='Comment', endpoint='comment')),
        (WishCommentAdmin, Comment, dict(
            category='Dev', name='Wish Comment', endpoint='wish_comment')),
        (ProductCommentAdmin, Comment, dict(
            category='Dev', name='Product Comment', endpoint='product_comment',
        )),
        (LikeAdmin, Like, dict(category='Dev')),
        (AllPostAdmin, Post, dict(category='Dev', name='全部Post')),
        (PostPhotoAdmin, PostPhoto, dict(
            category='Dev',
        )),
        (PaymentDevAdmin, Payment, dict(
            category='Dev', endpoint='dev_payment',
        )),
        (WishAdmin, Wish, dict(category='Wish')),
        (TipAdmin, Tip, dict(category='Wish')),
        (VoteAdmin, Vote, dict(category='Wish')),
        (VendorAdmin, Vendor, {}),
        (AdminUserAdmin, AdminUser, {}),
        (AdminRoleAdmin, AdminRole, {}),
        (PaymentAdmin, Payment, {}),
        (ConfAdmin, Conf, dict(
            name='客户端版本', category='配置',
        )),
        # 团购
        (CategoryAdmin, Category, dict(
            name='分类', category='商品',
        )),
        (ProductAdmin, Product, dict(
            name='商品', category='商品',
        )),
        (SpecAdmin, Spec, dict(
            name='规格名称', category='商品',
        )),
        (SpecOptionAdmin, SpecOption, dict(
            name='规格可选项', category='商品',
        )),
        (BatchSpecAdmin, BatchSpec, dict(
            name='批次规格', category='团购',
        )),
        (BatchAdmin, Batch, dict(
            name='批次', category='团购',
        )),
        (GameAdmin, Game, dict(
            name='期次', category='团购',
        )),
        (OrderAdmin, Order, dict(
            name='订单', category='团购',
        )),
    ]
    for model_view, model, kwargs in admin_model_view_args:
        admin.add_view(model_view(model, lazy_session, **kwargs))

    # tasks
    configure_celery(celery_app, app)

    return app
