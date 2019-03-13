from pd.tasks import logger


def deprecated():
    """
    Sometimes we need to remove task definitions. We can't simply remove them
    from code, since there might be tasks already enqueued.

    Recommended task retirement plan:
    - remove the implementation of the task. Optionally mark it as deprecated
      with this function.
    - check all the places that calls the task, including beat. Remove them
      so no new instance of the task are created
    - deploy this version of code. Old tasks will be consumed.
    - once we're sure all instances of the task are processed, the task
      definition can be safely removed
    """
    logger.warn(
        'this task is deprecated. It will be removed soon')
