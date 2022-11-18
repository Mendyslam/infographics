from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, re
from wtforms.validators import DataRequired

from app.models import User


class RegistrationForm(FlaskForm):
    """
    Defines fields and properties for Registration
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Ensuring unqiue username
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please provide a different username')

    def validate_email(self, email):
        """
        Ensuring unqiue email
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please provide a different email address')


class LoginForm(FlaskForm):
    """
    Defines fields of application Login form
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
