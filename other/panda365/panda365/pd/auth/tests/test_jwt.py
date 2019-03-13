import pytest
from pd.facebook.models import User
from ..jwt import (
    auth_required, current_user, current_user_data,
    Unauthorized, _decode_token, _create_token,
)


@pytest.fixture
def token(db_session, client):
    resp = client.post('/v1/auth/tokens/', json={
        'fb_token': 'fb_token'
    })
    assert resp.status_code == 200, resp.json
    return resp.json['jwt_token']


@pytest.fixture
def user(token, user_fb_id):
    return User.fb_query(user_fb_id).first()


@auth_required
def protected_view():
    pass


def test_create_token(app_context):
    payload = {
        'hi': 'ho'
    }
    secret = 'secret'
    token = _create_token(payload, secret)
    assert _decode_token(token, secret) == payload


def test_auth_required(app, token, user, user_fb_id):

    with app.test_request_context('/', headers={
        'Authorization': 'Bearer {}'.format(token)
    }):
        protected_view()
        assert current_user.fb_id == user_fb_id
        assert current_user._get_current_object() is user
        assert current_user_data['id'] == user.id


@pytest.mark.parametrize('auth_header', [
    None,
    '',
    'monkey',
    'Bearer',
    'Bearer token extra',
    'Bearer invalid_token',  # invalid token
    'Bearer {}'.format(_create_token(
        {'hi': 1}, 'secret', ttl=-1000)),  # expired
])
def test_auth_header_errors(app, auth_header, monkeypatch):
    monkeypatch.setitem(app.config, 'SECRET_KEY', 'secret')
    headers = {}
    if auth_header:
        headers['Authorization'] = auth_header

    with app.test_request_context('/', headers=headers):
        with pytest.raises(Unauthorized):
            protected_view()


def test_current_user_without_auth_required(app):
    with app.test_request_context('/'):
        assert current_user._get_current_object() is None
        assert current_user_data._get_current_object() is None
