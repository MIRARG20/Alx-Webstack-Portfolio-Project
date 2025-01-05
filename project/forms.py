from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project.models import Customer


# Form for user registration.
class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email = StringField(label='Email', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='Confirm_password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Sign Up')
    
    def validate_username(self, username):
        customer = Customer.query.filter_by(username=username.data).first()
        if customer:
            raise ValidationError('Username already exists')
        


# Form for user login.
class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    remember = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign in')