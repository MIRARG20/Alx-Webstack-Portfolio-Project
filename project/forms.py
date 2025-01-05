from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from project.models import Customer
from flask_wtf.file import FileField, FileRequired


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


# Form for adding new products to the store.
class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    product_picture = FileField('Product Picture', validators=[FileRequired()])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')


# Form for placing an order.
class CartForm(FlaskForm):
    submit = SubmitField('Place Order')