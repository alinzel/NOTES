from pd.groupon.factory import BatchFactory


def test_groupon_detail_page(db_session, client):
    batch = BatchFactory(country='MY')
    game = batch.create_game()
    db_session.commit()
    # order = OrderFactory(game=game)
    # other people's order

    url_tpl = '/my/groupon/{}.html'.format(game.batch_id)

    resp = client.get(url_tpl)
    assert resp.status_code == 200

    url_tpl = '/my/groupon/{}.html'.format(321123321)
    resp = client.get(url_tpl)
    assert resp.status_code == 404

    url_tpl = '/{}/groupon/1.html'.format('M')
    resp = client.get(url_tpl)
    assert resp.status_code == 404


def test_groupon_htp(db_session, client):
    url_tpl = '/htp.html'
    resp = client.get(url_tpl)
    assert resp.status_code == 200
