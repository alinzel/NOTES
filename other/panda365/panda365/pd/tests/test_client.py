from unittest.mock import patch
from flask import request, jsonify


def test_client_json(app, client):
    url = '/test_client_json'

    @app.route(url, methods=['post'])
    def test_json():
        assert request.headers['content-type'] == 'application/json'
        return jsonify(**request.get_json())

    data = {'a': 12}
    resp = client.post(url, json=data)
    assert resp.status_code == 200
    assert resp.json == data


def test_client_resp_text(app, client):
    url = '/test_client_resp_text'

    @app.route(url)
    def test_hi():
        return 'hi'

    resp = client.get(url)
    assert resp.text == 'hi'


def test_client_user(client, user):
    assert not client.user
    client.login(user)
    assert client.user == user
    with patch('pd.test_utils.BaseClient.open') as m:
        # auth header should be set if logged in
        client.get('/')
        headers = m.call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer {}'.format(client.token)

        # auth header in args takes precedence
        client.get('/', headers={'Authorization': 'blah'})
        headers = m.call_args[1]['headers']
        assert headers['Authorization'] == 'blah'

        # auth header should not be set if not logged in
        client.logout()
        assert not client.user
        client.get('/')
        headers = m.call_args[1].get('headers', {})
        assert 'Authorization' not in headers

        with client.auth_context(user) as cli:
            assert cli.user == user


def test_admin_client(admin_client):
    # can login & out
    assert admin_client.user_id
    admin_client.logout()
    assert not admin_client.user_id
