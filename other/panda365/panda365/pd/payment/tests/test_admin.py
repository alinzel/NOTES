def test_formate_link(admin_client, payment):
    resp = admin_client.get('/admin/payment/')
    assert resp.status_code == 200
    assert b'href="/admin/order/?flt_id_equals=' in resp.data
