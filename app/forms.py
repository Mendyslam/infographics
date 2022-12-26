from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.validators import DataRequired, Length

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


class EditProfileForm(FlaskForm):
    """
    Edit user profile
    """
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, current_username, *args, **kwargs):
        """
        Modify form instantiation to assign current_username attribute to instance
        """
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.current_username = current_username

    def validate_username(self, username):
        """
        Checks if the new username does not already exist in the database
        """
        if username.data != self.current_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class FollowForm(FlaskForm):
    """
    Follow calls
    """
    submit = SubmitField('submit')


class PostForm(FlaskForm):
    """
    Create a Post
    """
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
