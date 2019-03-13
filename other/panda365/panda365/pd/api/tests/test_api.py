from unittest.mock import patch
from pd.api import handle_422


def test_api_index(client):
    resp = client.get('/v1/')
    assert resp.status_code == 200
    assert resp.json['endpoints']
    # cors
    assert resp.headers['Access-Control-Allow-Origin'] == '*'

    resp = client.get('/v1/docs.html')
    assert resp.status_code == 200


def test_report_422(app, monkeypatch):
    monkeypatch.setitem(app.config, 'API_ENDPOINTS_REPORT_422', {'api.index'})
    with app.test_request_context('/v1/', data=dict(password=1)):
        with patch('pd.api.current_app.logger.error') as error_log:
            handle_422(ValueError('mock error'))
        assert error_log.called
        assert 'password' in str(error_log.call_args)
