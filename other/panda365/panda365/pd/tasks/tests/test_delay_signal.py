from blinker import signal
from unittest.mock import patch, Mock
from pd.tasks.tasks import delay_signal

test_signal = signal('test')


def test_delay_signal(app):
    event = Mock()
    with patch('pd.tasks.tests.test_delay_signal.test_signal.send'):
        delay_signal('test', event)
        # should be able to identify the signal by name
        assert test_signal.send.called
