from flask import abort, current_app, jsonify, request
from werkzeug.exceptions import default_exceptions
from .json import JSONEncoder  # noqa
from .io import io_annotated, SerializationError  # noqa


def abort_json(code, message=None, errors=None):
    '''
    Unlike flask.abort, this function does not raise an HTTPException.
    Instead it returns a jsonfied resp.
    '''
    if not message:  # use generic description from werkzeug
        exp = default_exceptions[code]()
        message = '{}: {}'.format(exp.name, exp.description)
    data = dict(message=message)
    if errors:
        data['errors'] = errors
    resp = jsonify(**data)
    resp.status_code = code
    abort(code, response=resp)


def handle_422(err):
    try:
        errors = err.exc.messages
    except AttributeError:
        errors = None
    if request.endpoint in current_app.config['API_ENDPOINTS_REPORT_422']:
        current_app.logger.error(
            'unexpected 422 error on endpoint %s; data: %s',
            request.endpoint, [item for item in request.values.items()],
        )
    return jsonify(
        message='Unprocessable Entity',
        # errors=errors,
        errors=errors,
    ), 422


def handle_marshmallow_validation_error(err):
    return jsonify(
        message='Unprocessable Entity',
        errors=err.messages,
    ), 422


def handle_serialization_error(serialization_error):
    validation_err = serialization_error.error
    resp = jsonify(
        message='Serialization Error',
        errors=getattr(validation_err, 'messages', None),
    )
    resp.status_code = 500
    current_app.logger.exception(
        'serialization error: %s', serialization_error)
    return resp
