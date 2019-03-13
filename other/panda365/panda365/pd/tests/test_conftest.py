from unittest.mock import patch, MagicMock
import pytest
# from pd.conftest import db


@pytest.mark.parametrize('db_exists,reset_db,expect_create', [
    [True, True, True],
    [False, True, True],
    [True, False, False],
    [False, False, True],
])
def test_reset_db(app, db_exists, reset_db, expect_create):
    request = MagicMock()
    request.config.getoption.return_value = reset_db
    # db cannot be imported at the module level, cause then pytest would
    # think we're "defining" it here
    from pd.conftest import db
    with patch('pd.conftest.su') as mock_su:
        mock_su.database_exists.return_value = db_exists
        with patch('pd.conftest._create_db') as mock_create_db:
            db(app, request)
            assert mock_create_db.called == expect_create


@pytest.mark.parametrize('schema_mode', ['alembic', 'sqla'])
def test_create_db_mode(app, schema_mode):
    request = MagicMock()
    request.config.getoption.return_value = schema_mode
    from pd.conftest import db
    with patch('pd.conftest.su') as mock_su:
        with patch('pd.conftest._db') as mock_db:
            with patch('pd.conftest.flask_migrate') as mock_migrate:
                db(app, request)
                assert mock_su.create_database.called
                if schema_mode == 'alembic':
                    assert mock_migrate.upgrade.called
                else:
                    assert mock_db.create_all.called


def test_db_session(db_session):
    r = db_session.execute('select current_database() as db')
    assert r.fetchone().db.startswith('panda365_test')
