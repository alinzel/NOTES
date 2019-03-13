from flask_security.forms import Required, Length
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class LoginForm(FlaskForm):
    account = StringField('Account', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')
