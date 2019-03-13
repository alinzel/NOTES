import os
from unittest.mock import patch

import flask_migrate
import pytest
from redis import Redis
import sqlalchemy as sa
import sqlalchemy_utils as su

from pd.app import create_app
from pd.admin.factory import AdminUserFactory
from pd.facebook.factory import UserFactory
from pd.config import TestConfig
from pd.sqla import db as _db
from pd.test_utils import AdminClient, Client, Response


def pytest_addoption(parser):
    parser.addoption(
        '--reset-db', action='store_true', default=False,
        help='If False, create test database only if it does not exist. '
             'Otherwise always re-create db. Default: False'
    )
    parser.addoption(
        '--schema-mode', action='store', default='sqla',
        choices=('sqla', 'alembic'),
        help='how to initialize test database schema in tests. ' +
        'sqla: db.create_all() - fast; can run without migrations. ' +
        'alembic: run migrations - slower but necessary if tests rely ' +
        'on data migrations'
    )


def _create_db(db_url, mode):
    su.create_database(db_url)
    assert mode in ('sqla', 'alembic')
    print('initialize db schema with {}..'.format(mode))
    if mode == 'alembic':
        flask_migrate.upgrade()
    else:
        _db.create_all()


@pytest.fixture(scope='session')
def app(request):
    _app = create_app(
        'Test',
        SQLALCHEMY_DATABASE_URI='{}_{}'.format(
            TestConfig.SQLALCHEMY_DATABASE_URI,
            request.config.getoption('--schema-mode')
        )
    )
    _app.test_client_class = Client
    _app.response_class = Response
    return _app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture
def admin_user(db_session):
    return AdminUserFactory(email='admin@test.com', password='123456')


@pytest.fixture
def admin_client_clean(app):
    """
    test client used to test admin views
    """
    return AdminClient(app, app.response_class, use_cookies=True)


@pytest.fixture
def admin_client(app, admin_user, admin_client_clean):
    """
    an admin client that is logged in as admin_user
    """
    admin_client_clean.login(admin_user.email, admin_user.password)
    assert admin_client_clean.user_id == admin_user.id
    return admin_client_clean


@pytest.fixture(scope='session')
def db(app, request):
    """
    create test database and schema if necessary
    """
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    with app.app_context():
        if request.config.getoption('--reset-db'):
            if su.database_exists(db_url):
                print('database exists: {}; drop it..'.format(db_url))
                su.drop_database(db_url)
            print('create database {}..'.format(db_url))
            _create_db(db_url, request.config.getoption('--schema-mode'))
        else:
            # only create new database if it does not exist
            if su.database_exists(db_url):
                print('database exists: {}; reuse it..'.format(db_url))
            else:
                print('database does not exist: {}; create..'.format(db_url))
                _create_db(db_url, request.config.getoption('--schema-mode'))
    return _db


@pytest.fixture(scope='function')
def db_session(app, app_context, db):
    """
    Creates a new database session for a test. Note you must use this fixture
    if your test connects to db.

    see http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
        #joining-a-session-into-an-external-transaction-such-as-for-test-suites

    Here we not only support commit calls but also rollback calls in tests,
    :coolguy:.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds=db.get_binds(app))
    session = db.create_scoped_session(options=options)

    session.begin_nested()

    # session is actually a scoped_session
    # for the `after_transaction_end` event, we need a session instance to
    # listen for, hence the `session()` call
    @sa.event.listens_for(session(), 'after_transaction_end')
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.expire_all()
            session.begin_nested()

    db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user(db_session):
    return UserFactory()


@pytest.fixture
def png_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'ok.png'))


@pytest.fixture
def gif_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'tiny.gif'))


@pytest.fixture
def png_data_url():
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAADCAIAAAA7ljmRAAAAGElEQVQIW2P4DwcMDAxAfBvMAhEQMYgcACEHG8ELxtbPAAAAAElFTkSuQmCC'  # noqa


def pytest_configure(config):
    # register markers
    config.addinivalue_line(
        'markers', 'db: mark test as using the database.'
    )


@pytest.fixture(autouse=True)
def _db_mark(request):
    if request.node.get_marker('db'):
        request.getfixturevalue('db_session')


@pytest.fixture
def clean_redis(app):
    """
    ensure redis is clean
    """
    r = Redis.from_url(app.config['CELERY_BROKER_URL'])
    return r.flushdb()


# we don't touch s3 in tests
@pytest.fixture(autouse=True)
def mock_boto_s3():
    with patch('pd.s3.s3') as m:
        yield m


@pytest.fixture
def s3_storage_mock(app, monkeypatch):
    with patch(
        'pd.admin.fields.s3ext.store',
        region=app.config['S3_REGION'],
        bucket_name=app.config['S3_BUCKET'],
    ) as m:
        m.path_exists.return_value = False
        yield m


@pytest.fixture
def model_admin_render_mock():
    with patch(
        'flask_admin.model.base.BaseModelView.render',
            return_value='mocked render response') as m:
        yield m
