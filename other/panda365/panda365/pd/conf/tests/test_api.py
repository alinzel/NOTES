from pd.test_utils import assert_dict_like
from pd.conf.factory import ConfFactory


def test_get(client, db_session):
    conf = ConfFactory()
    url_tpl = '/v1/conf/{}'
    resp = client.get(url_tpl.format(conf.name))
    assert resp.status_code == 200
    assert_dict_like(resp.json, {
        'name': conf.name,
        'min_version': conf.min_version,
        'latest_version': conf.latest_version,
        'description': conf.description,
    })

    resp = client.get(url_tpl.format('blah'))
    assert resp.status_code == 404
