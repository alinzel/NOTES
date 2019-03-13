from pd.i18n import get_timezone


def test_get_locale(app, monkeypatch, admin_client):
    # if no accept-language is sent, the default locale should be en
    resp = admin_client.get('/admin/')
    assert 'Home' in resp.text
    # should respect accept-language
    resp = admin_client.get('/admin/', headers={
        'Accept-Language': 'zh-CN;q=0.8,en;q=0.6'
    })
    assert '首页' in resp.text


def test_get_timezone(app):
    with app.test_request_context('/'):
        assert get_timezone() is None
    with app.test_request_context('/admin/'):
        assert get_timezone() == 'Asia/Shanghai'
