from functools import wraps, partial

from celery import current_task
from requests.exceptions import Timeout, ConnectionError, HTTPError


class retriable:
    """
    a decorator to allow a task to be retried.

    :params exceptions:
        a list of exceptions that are considered retriable

    Example::

        @celery.task
        @retriable([ConnectionError])
        def get_google():
            requests.get('https://google.com')

    The above would retry the task if there's any network error
    """
    def __init__(self, exceptions, max_retries=None, delay=60):
        self.exceptions = tuple(exceptions)
        self.max_retries = max_retries
        self.delay = delay

    def on_exception(self, e):
        raise current_task.retry(
            exc=e, max_retries=self.max_retries, countdown=self.delay)

    def __call__(self, func):

        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                self.on_exception(e)

        return inner


requests_retriable = partial(retriable, exceptions=[Timeout, ConnectionError])


class requests_retriable(retriable):

    def __init__(
        self, exceptions=(Timeout, ConnectionError),
            status_codes=(502, 503, 504), **kwargs):
        exceptions = exceptions or self.DEFAULT_EXCEPTIONS
        if status_codes:
            exceptions = list(exceptions) + [HTTPError]
            self.status_codes = set(status_codes)
        else:
            self.status_codes = []
        super().__init__(exceptions, **kwargs)

    def on_exception(self, e):
        if isinstance(e, HTTPError) and (
                e.response.status_code not in self.status_codes):
            raise
        super().on_exception(e)
