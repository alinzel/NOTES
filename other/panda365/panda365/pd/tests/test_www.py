def test_www(client):
    resp = client.get('/favicon.ico')
    assert resp.status_code == 200

    resp = client.get('/')
    assert resp.status_code == 200
