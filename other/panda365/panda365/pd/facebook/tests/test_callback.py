import pytest


URL = '/facebook/'


@pytest.fixture
def verify_query(config):
    return {
        'hub.mode': 'subscribe',
        'hub.challenge': 'challenge',
        'hub.verify_token': config['FACEBOOK_VERIFY_TOKEN'],
    }


def test_verify(client, verify_query):
    resp = client.get(URL, query_string=verify_query)
    assert resp.status_code == 200
    assert resp.text == 'challenge'


@pytest.mark.parametrize('error_field,error_data', [
    ['hub.mode', 'only subscribe is allowed'],
    ['hub.verify_token', 'some fake token'],
    ['hub.verify_token', None],
    ['hub.mode', None],
    ['hub.challenge', None],
])
def test_verify_error(client, verify_query, error_field, error_data):
    if error_data is None:
        verify_query.pop(error_field)
    else:
        verify_query[error_field] = error_data
    resp = client.get(URL, query_string=verify_query)
    assert resp.status_code == 422


@pytest.fixture
def update_payload():
    return b'{"entry": [{"changes": [{"field": "feed", "value": {"item": "status", "sender_name": "Panda365", "sender_id": 286247441793403, "post_id": "286247441793403_286255828459231", "verb": "add", "published": 1, "created_time": 1489479249, "message": "test hook3"}}], "id": "286247441793403", "time": 1489479252}], "object": "page"}'  # noqa


@pytest.mark.parametrize('signature,expected_status', [
    ['sha1=342fd607f8645f4659e6d1d7190dee0ce94cda33', 200],
    ['sha1=dafasdfadsadfasdfef4ewefw4erpoiwrejgoijr', 422],
])
def test_update(
        client, update_payload, signature, expected_status, mock_signal,
        app, monkeypatch):
    # the signature is generated with those creds
    monkeypatch.setitem(app.config, 'FACEBOOK_APP_ID', '294505760966825')
    monkeypatch.setitem(
        app.config, 'FACEBOOK_APP_SECRET', '186c3793f3121c15daa5bad4ed332419')
    mock_signal.return_value.send.return_value = [
        ('fake_receiver', 'fake_result')]
    resp = client.post(URL, data=update_payload, headers={
        'X-Hub-Signature': signature,
        'Content-Type': 'application/json'
    })
    assert resp.status_code == expected_status, resp.json
