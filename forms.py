from cProfile import label
import email
from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from .models import User


class RegisterForm(FlaskForm):
    def validate_username(self,username_to_check):
        user = User.query.filter_by(user_name=username_to_check.data).first()       #phải có .data
        if user:
            raise ValidationError('Username already exists')

    def validate_email(self,email_to_check):
        email = User.query.filter_by(user_email=email_to_check.data).first()
        if email:
            raise ValidationError('Email already exists')

    username = StringField(label='Username:', validators=[Length(min=2, max=30), DataRequired()])
    fullname = StringField(label='Full Name:', validators=[Length(min=2, max=40), DataRequired()])      
    email = StringField(label='Email:',  validators=[Email(),  DataRequired()])
    phone = StringField(label='Phone Number:', validators=[Length(min=8, max=12), DataRequired()])      
    password1 = PasswordField(label='Password:', validators=[Length(min=5),  DataRequired()])
    password2 = PasswordField(label='Confirm Password:',  validators=[EqualTo('password1'), DataRequired()])
    #check password có giống nhau không ở đây
    submit = SubmitField(label='Sign Up')

class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Log In')

class PurchaseForm(FlaskForm):
    submit = SubmitField(label='Purchase')

# class SellForm(FlaskForm):
#     submit = SubmitField(label='Sell')

class AddForm(FlaskForm):
    fullname = StringField(label='Student Name:', validators=[DataRequired()])
    studentID = StringField(label='Student ID:', validators=[DataRequired()])
    price = StringField(label='Price:', validators=[DataRequired()])
    submit = SubmitField(label='Add')

