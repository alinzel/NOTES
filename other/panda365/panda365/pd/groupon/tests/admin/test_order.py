from pd.groupon.factory import BatchFactory, OrderFactory


def test_order_admin(admin_client, user, db_session):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    OrderFactory(user=user, game=game)
    resp = admin_client.get('/admin/order/')
    # test product link
    assert resp.status_code == 200
    assert b'href="/admin/product/?flt_id_equals=' in resp.data
    # test export
    resp = admin_client.get('/admin/order/export/csv')
    assert resp.status_code == 200
    assert b'Product Id' in resp.data
