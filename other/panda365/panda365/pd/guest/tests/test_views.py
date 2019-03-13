from pd.facebook.factory import UserFactory, CommentFactory
from pd.guest.models import GuestUsers


def test_guest_login(db_session, client):
    guest_user = GuestUsers(id='88888', account='kangqiantech', pw='123456')
    db_session.add(guest_user)

    assert guest_user

    url_tpl = '/comments_reply/login.html'
    resp = client.post(url_tpl, data={
        'account': 'kangqiantech',
        'password': '123456'
    })
    assert resp.status_code == 302

    resp = client.post(url_tpl, data={
        'account': 'kangqian',
        'password': '123456'
    })
    assert resp.status_code == 200

    resp = client.get(url_tpl)
    assert resp.status_code == 200

    url_tpl = '/comments_reply/comments.html'
    resp = client.get(url_tpl)
    assert resp.status_code == 200

    comment = CommentFactory()
    db_session.commit()
    url_reply = '/comments_reply/reply/'
    resp = client.post(url_reply, data={
        'id': comment.id,
        'message': 'yangshuyu'
    })
    assert resp.status_code == 200

    UserFactory(id=7068)
    db_session.commit()
    url_reply = '/comments_reply/reply/'
    resp = client.post(url_reply, data={
        'id': comment.id,
        'message': 'yangshuyu'
    })
    assert resp.status_code == 200


def test_guest_comments(db_session, client):
    guest_user = GuestUsers(account='kangqiantech', pw='123456')
    db_session.add(guest_user)

    url_tpl = '/comments_reply/comments.html'
    resp = client.get(url_tpl)
    assert resp.status_code == 302
