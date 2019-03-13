from celery.app.task import Task
from flask import _app_ctx_stack


class FlaskTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        """
        here we make sure the task is run in an app context.
        """
        if _app_ctx_stack.top:
            # the task is called called eagerly in a view, there is already
            # an app context, directly call the task
            return super().__call__(*args, **kwargs)
        else:
            # the task is called asyncly in a worker, create app context
            # for it
            with self._app.flask_app.app_context():  # pragma: no cover
                return super().__call__(*args, **kwargs)
