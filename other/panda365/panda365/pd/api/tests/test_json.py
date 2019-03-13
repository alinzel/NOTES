import json
import arrow
import pytest
from werkzeug.exceptions import HTTPException
from .. import abort_json
from ..json import JSONEncoder


def test_encode_arrow():
    encoder = JSONEncoder()
    data = {
        'whatever': 10,
        'now': arrow.get('2017-01-01 00:00:00').to('+08:00')
    }
    assert json.loads(encoder.encode(data)) == {
        'whatever': 10,
        'now': '2017-01-01T08:00:00+08:00'
    }


@pytest.mark.parametrize('args,expected_message,expected_errors', [
    [[], 'Bad Request', None],
    [['hi'], 'hi', None],  # custom message
    # errors
    [['hi', [{'value': 'required'}]], 'hi', [{'value': 'required'}]],
])
def test_abort_json(
        app_context, args, expected_message, expected_errors):
    with pytest.raises(HTTPException) as exc_info:
        abort_json(400, *args)
    resp = exc_info.value.response
    assert resp.status_code == 400
    assert resp.content_type == 'application/json'
    assert expected_message in resp.json['message']
    assert resp.json.get('errors', None) == expected_errors
