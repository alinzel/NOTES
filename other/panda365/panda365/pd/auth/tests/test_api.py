from unittest.mock import patch
import arrow
import jwt
from facebook import GraphAPIError
from pd.facebook.models import User
from pd.test_utils import assert_dict_like, Any


def test_create_token(db_session, client, mock_fb_graph):
    for _ in range(2):
        resp = client.post('/v1/auth/tokens/', json={
            'fb_token': 'some_fb_token',
        })
        assert resp.status_code == 200
        # a user should be created for this token
        user = User.query.filter_by(fb_id='285859391846526').one()
        # the access token should be fetched or refreshed
        assert not user.token_expire_soon()

        # a jwt token should be returned to the client
        token = resp.json['jwt_token']
        payload = jwt.decode(token, verify=False)
        assert_dict_like(payload, {
            'name': user.name,
            'icon_url': user.icon_url,
            'id': user.id,
            'exp': Any(int),  # token should expire in a while
        })


def test_invalid_token(db_session, client, mock_fb_graph):
    mock_fb_graph.get_object.side_effect = GraphAPIError(
        'Invalid OAuth access token')

    resp = client.post('/v1/auth/tokens/', json={
        'fb_token': 'fake_fb_token'
    })
    assert resp.status_code == 403, resp.text
    assert 'Invalid OAuth access token' in resp.json['message']


def test_extend_token(db_session, client, mock_fb_graph):
    resp = client.post('/v1/auth/tokens/', json={
        'fb_token': 'some_fb_token',
    })
    assert resp.status_code == 200
    token = resp.json['jwt_token']
    payload = jwt.decode(token, verify=False)

    resp = client.post('/v1/auth/tokens/refresh/')
    assert resp.status_code == 401

    # refresh the token 10 seconds after it's created
    with patch(
            'pd.auth.jwt.arrow.utcnow',
            return_value=arrow.utcnow().replace(seconds=10)):
        resp = client.post('/v1/auth/tokens/refresh/', headers={
            'Authorization': 'Bearer {}'.format(token)
        })
    assert resp.status_code == 200
    new_token = resp.json['jwt_token']
    # token should be refreshed
    assert new_token != token
    new_payload = jwt.decode(new_token, verify=False)
    # the new token should represent the same user
    assert payload['id'] == new_payload['id']
    # the new token should expire later
    assert payload['exp'] < new_payload['exp']
