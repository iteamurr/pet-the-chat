"""
    This module is responsible for the presentation of forms.
"""

from hashlib import md5

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError
from safe import check

from .models import User


class RegistrationForm(FlaskForm):
    """User registration form model."""

    username = StringField(
        "username_field",
        validators=[
            InputRequired("Username can't be empty."),
            Length(min=2, message="Username must be at least 2 characters long."),
            Length(max=40, message="Username can't be more than 40 characters."),
        ],
    )
    password = PasswordField(
        "password_field",
        validators=[
            InputRequired("Password can't be empty."),
            Length(min=8, message="Password must be at least 8 characters long."),
            Length(max=50, message="Password can't be more than 50 characters."),
        ],
    )
    confirm_pswd = PasswordField(
        "confirm_pswd_field",
        validators=[
            InputRequired("Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("There is already a user with this name.")

    def validate_password(self, password):
        strength = check(str(password.data))
        if not bool(strength):
            raise ValidationError(f"{str(strength).capitalize()}.")


class LoginForm(FlaskForm):
    """User login form model."""

    username = StringField("username_field", validators=[InputRequired()])
    password = PasswordField("password_field", validators=[InputRequired()])
    submit = SubmitField("Login")

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        hash_pswd = md5(str(password.data).encode("utf-8")).hexdigest()
        if (user is None) or (hash_pswd != user.password):
            raise ValidationError("Wrong email or password.")
