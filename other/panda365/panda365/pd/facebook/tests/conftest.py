from unittest.mock import patch
import arrow
import pytest


@pytest.fixture
def mock_signal():
    with patch('pd.facebook.parser.signal') as m:
        yield m


@pytest.fixture
def default_kwargs():
    return dict(page_id='page_id', time=arrow.utcnow())
