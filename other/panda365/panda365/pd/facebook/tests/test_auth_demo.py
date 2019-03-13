def test_auth_demo(client):
    resp = client.get('/facebook/_auth_demo.html')
    assert resp.status_code == 200
