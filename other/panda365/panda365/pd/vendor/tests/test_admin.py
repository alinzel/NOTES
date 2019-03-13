from pd.vendor.factory import VendorFactory


def test_list_view(admin_client, db_session):
    # add some vendors to display
    VendorFactory.create_batch(2)
    resp = admin_client.get('/admin/vendor/')
    assert resp.status_code == 200
