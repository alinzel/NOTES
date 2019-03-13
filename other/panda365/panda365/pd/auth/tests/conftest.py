from unittest.mock import patch
import pytest


@pytest.fixture
def user_fb_id():
    return '285859391846526'


@pytest.fixture(autouse=True)
def mock_fb_graph(user_fb_id):
    with patch('pd.auth.api.graph_factory') as m:
        graph = m.return_value

        graph.extend_access_token.return_value = {
            'access_token': 'EAAEL2fdESKkBAEkFRWZC30eILMgkWoErxeelKd4ZCfKLUy9jdCO97drnDZA5Md6uBr4oMQeiMNoXplwnSmizRKuGPbkeQXlv6sv3XcSwvWSo1orUJQD1xoUCjgIrE36EsVL9HhBFG8U0bOyCy9WjGc1ynE7Q3EZD',  # noqa
            'expires_in': 5182899,
            'token_type': 'bearer'
        }
        graph.get_object.return_value = {
            'id': user_fb_id,
            'name': 'Harry Liang',
        }
        yield graph
