from flask import url_for
from flask_security.utils import login_user
import pytest
from pd.admin.base import SecurityMixin
from pd.admin.factory import AdminUserFactory
from pd.ext import mail


@pytest.mark.parametrize('email,should_send_confirm_email', [
    ['asdf', False],
    ['', False],
    ['a@fake.com', False],
    ['a@test.com', True],
])
def test_register(db_session, client, email, should_send_confirm_email):
    with mail.record_messages() as outbox:
        client.post('/admin/auth/register', data={
            'email': email,
            'password': '123456'
        })
        assert bool(outbox) == should_send_confirm_email


def test_access(db_session, app):
    s = SecurityMixin()
    user = AdminUserFactory(active=False)
    with app.test_request_context('/'):
        assert not s.is_accessible()
        # should redirect user to login
        resp = s.inaccessible_callback('test')
        assert resp.location.startswith(url_for('security.login'))

        login_user(user)
        # user is not active
        assert not s.is_accessible()

        user.active = True
        login_user(user)
        assert s.is_accessible()
