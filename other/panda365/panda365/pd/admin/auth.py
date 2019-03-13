from flask import current_app
from flask_security import ConfirmRegisterForm as _ConfirmRegisterForm
from wtforms import ValidationError


class ConfirmRegisterForm(_ConfirmRegisterForm):

    def validate_email(self, field):
        if field.errors:
            return
        domain = field.data.split('@')[1]
        if domain != current_app.config['SECURITY_ACCOUNT_DOMAIN']:
            raise ValidationError(
                'only emails from "{}" is allowed to register'.format(
                    current_app.config['SECURITY_ACCOUNT_DOMAIN'])
            )
