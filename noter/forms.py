from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, validators
from wtforms.validators import DataRequired


class loginForm(Form):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class signupForm(Form):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirmPass', message='Passwords must match')
    ])
    confirmPass = PasswordField('Confirm Password', validators=[DataRequired()])


class entryForm(Form):
    title = StringField('Title')
    body = TextAreaField('Text', validators=[DataRequired()])
