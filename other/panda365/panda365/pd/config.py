import ast
import os
from pd.utils import get_by_prefix


required = object()


class DevConfig:
    ENV = 'dev'
    DEBUG = True
    NUM_PROXIES = 0
    LOGGING_LEVEL = 'INFO'
    SECRET_KEY = 'secret key'
    SERVER = 'localhost:5000'
    # set in Nginx; this is only for help text. Unit: MB
    CLIENT_MAX_BODY_SIZE = 50
    # docs
    DOCS_ENABLE_TEST_CLIENT = True
    # api
    API_PER_PAGE = 20
    # 422 errors from those endpoints should be logged and report to sentry
    # this is useful for the endpoints which should not fail normally, like
    # callback endpoints from payment services
    API_ENDPOINTS_REPORT_422 = {
        'payments_payssion.callback',
        'payments_payssion.notify',
    }
    # facebook
    FACEBOOK_VERIFY_TOKEN = 'fb_verify_token'
    FACEBOOK_APP_ID = '307155839701817'
    FACEBOOK_APP_SECRET = 'dc92e036e3c1bc51a3e0be8e9ebd55da'
    # debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/panda365'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jwt
    JWT_TTL = 86400 * 7
    JWT_LEEWAY = 0
    # aws s3
    AWS_KEY_ID = 'AKIAJPLRBWTHMGGTT54A'
    AWS_KEY_SECRET = '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'
    S3_REGION = 'ap-southeast-1'
    S3_BUCKET = 'static-dev.panda365.com'
    # cache-control for objects uploaded to s3 from admin
    S3_OBJ_MAX_AGE = 86400 * 7  # 7 days by default
    # datadog
    DD_SAMPLE_RATE = 1
    # sentry
    SENTRY_DSN = ''
    # security
    SECURITY_CLI_USERS_NAME = 'admin_users'
    SECURITY_CLI_ROLES_NAME = 'admin_roles'
    SECURITY_EMAIL_SENDER = 'no-reply@panda365.com'
    SECURITY_URL_PREFIX = '/admin/auth'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = 'salt'
    SECURITY_POST_LOGIN_VIEW = '/admin/'
    SECURITY_POST_LOGOUT_VIEW = '/admin/'

    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome to Panda 365 Admin'
    # admin
    SECURITY_ACCOUNT_DOMAIN = 'dev.com'
    # mail
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    # posts
    PAGE_USER_NAME = 'Panda365'
    # admin
    ADMIN_TIMEZONE = 'Asia/Shanghai'
    # babel
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh_cn', 'ms', 'id']
    # locale of content sync from facebook
    BABEL_FACEBOOK_LOCALE = 'en'
    # rate limit
    RATELIMIT_ENABLED = True
    # RATELIMIT_STORAGE_URL = 'redis://localhost/9'
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_SWALLOW_ERRORS = False

    # datadog
    STATSD_SAMPLE_RATE = 1
    # 团购
    # 团购结束后，支付处理中的订单不会被立即关闭，留给用户一些时间完成支付
    # 这个配置定义了在批次结束后，如果用户在下面的时间以后仍未完成支付，
    # 则将订单设置为取消
    PAYMENT_PROCESSING_ORDER_LINGER = 3600  # 1 hour
    # 支付
    PAYMENT_ENABLED_VENDORS = (
        'payssion',
    )
    # sandbox; app not activated yet
    # PAYSSION_API_KEY = 'd0f7c7150405abbf'
    # PAYSSION_API_SECRET = 'c88fca79f58ed27e1946d7c47ec34d24'
    # PAYSSION_IS_SANDBOX = True
    PAYSSION_API_KEY = 'k'
    PAYSSION_API_SECRET = 'v'
    PAYSSION_IS_SANDBOX = True

    # celery
    # CELERY_BROKER_URL = 'redis://localhost/10'
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,
    }
    CELERY_TASK_ACKS_LATE = True
    CELERY_WORKER_DISABLE_RATE_LIMITS = True
    CELERY_WORKER_CONCURRENCY = 2
    CELERY_WORKER_PREFETCH_MULTIPLIER = 4
    CELERY_TASK_TIME_LIMIT = 300  # 5min
    CELERY_WORKER_LOG_COLOR = False


class TestConfig(DevConfig):
    # tests make certain assumptions and here are they:
    ENV = 'test'
    ADMIN_TIMEZONE = 'Asia/Shanghai'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh_cn']
    BATCH_IMMINENT_TIME = 3600
    # CELERY_BROKER_URL = 'redis://localhost/11'
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DOCS_ENABLE_TEST_CLIENT = False
    RATELIMIT_ENABLED = False
    SECURITY_ACCOUNT_DOMAIN = 'test.com'
    SECURITY_PASSWORD_HASH = 'plaintext'
    SQLALCHEMY_DATABASE_URI = DevConfig.SQLALCHEMY_DATABASE_URI + '_test'
    TESTING = True
    WTF_CSRF_ENABLED = False


class DeployConfig(DevConfig):
    ENV = 'deploy'
    DEBUG = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    DOCS_ENABLE_TEST_CLIENT = False
    LOGGING_LEVEL = 'INFO'
    PREFERRED_URL_SCHEME = 'https'
    SECRET_KEY = required
    SERVER = required
    SQLALCHEMY_DATABASE_URI = required

    AWS_KEY_ID = required
    AWS_KEY_SECRET = required
    S3_BUCKET = required

    SENTRY_DSN = required
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = required
    SECURITY_ACCOUNT_DOMAIN = required

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = required
    MAIL_PASSWORD = required

    CELERY_BROKER_URL = required
    PAYMENT_PROCESSING_ORDER_LINGER = 3600  # 1 hour

    RATELIMIT_SWALLOW_ERRORS = True
    RATELIMIT_STORAGE_URL = required

    PAYSSION_API_KEY = required
    PAYSSION_API_SECRET = required
    PAYSSION_IS_SANDBOX = False


def load_config(app, name_or_cls=None, prefix='PD_', **kwargs):
    if not name_or_cls:
        name_or_cls = os.environ.get('PD_ENV', 'DEV')
    if isinstance(name_or_cls, str):
        name = '{}Config'.format(name_or_cls.title())
        try:
            config_cls = globals()[name]
        except KeyError:
            raise RuntimeError('{} is not defined'.format(name))
    else:
        config_cls = name_or_cls
    app.config.from_object(config_cls)
    app.config.from_envvar('PANDA_CONFIG', True)

    envvars = {}
    for k, v in get_by_prefix(os.environ, prefix).items():
        try:
            v = ast.literal_eval(v)
        except ValueError:
            pass
        envvars[k] = v
    app.config.update(envvars)

    app.config.update(**kwargs)

    # check for missing required config
    for k, v in app.config.items():
        if v is required:
            raise RuntimeError(
                'required configuration "{}" is not set', k)
