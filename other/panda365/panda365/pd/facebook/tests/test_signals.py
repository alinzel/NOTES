from blinker import signal, ANY
import pytest


@pytest.mark.parametrize('name,expected_receiver', [
    ['fb_post_add', 'add_post'],
    ['fb_post_edited', 'edit_post'],
    ['fb_post_remove', 'remove_post'],
    ['fb_comment_add', 'add_comment'],
    ['fb_comment_edited', 'edit_comment'],
    ['fb_comment_remove', 'remove_comment'],
    ['fb_like_add', 'add_like'],
    ['fb_like_remove', 'remove_like'],
])
def test_signals_connected(name, expected_receiver):
    assert expected_receiver in [  # pragma: no cover
        r.__name__ for r in signal(name).receivers_for(ANY)]
