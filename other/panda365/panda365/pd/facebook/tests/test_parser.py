from unittest.mock import patch
import arrow
import pytest
from ..parser import parse_change, parse_update


@pytest.mark.parametrize('kwargs,expected_entity', [
    [{'item': 'status'}, 'post'],
    [{'item': 'photo'}, 'post'],
    [{'item': 'post'}, 'post'],
    [{'item': 'like'}, 'like'],
    [{'item': 'reaction'}, None],
    [{'item': 'comment', 'post_id': 'post', 'parent_id': 'post'}, 'comment'],
    [{'item': 'comment', 'post_id': 'post', 'parent_id': 'c1'}, 'comment'],
])
def test_entity(
        app_context, kwargs, expected_entity, default_kwargs, mock_signal):
    change = {
        'field': 'feed',
        'value': {
            'item': 'status',
            'parent_id': 'parent',
            'post_id': 'post_id',
            'verb': 'add',
        }
    }
    change['value'].update(kwargs)
    parse_change(change, **default_kwargs)
    if expected_entity:
        signal_name = mock_signal.call_args[0][0]
        assert signal_name.startswith('fb_{}'.format(expected_entity))
        args, kwargs = mock_signal.return_value.send.call_args
        assert args == (change['value'],)
        assert kwargs == default_kwargs
    else:
        assert not mock_signal.called


def test_uninterested_topic(default_kwargs, mock_signal):
    parse_change({'field': 'blah'}, **default_kwargs)
    assert not mock_signal.called


def test_parse_update():
    fake_change = {}
    data = {
        'entry': [{
            'changes': [fake_change],
            'id': '286247441793403',
            'time': 1489996743,
        }],
        'object': 'page',
    }
    with patch('pd.facebook.parser.parse_change') as mock_parse_change:
        parse_update(data)
        assert mock_parse_change.called
        args, _ = mock_parse_change.call_args
        assert args == (fake_change, '286247441793403', arrow.get(1489996743))

    # object other than page
    data['object'] = 'user'
    with patch('pd.facebook.parser.parse_change') as mock_parse_change:
        parse_update(data)
        assert not mock_parse_change.called
