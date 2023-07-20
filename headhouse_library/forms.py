from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, TextAreaField, SelectField, URLField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo

class BudgetForm(FlaskForm):
    amount = FloatField(
        "Amount",
        validators=[InputRequired(),
                    NumberRange(min=0, message="Dont add empty expense")
        ]
    )

    submit = SubmitField("Set Budget")


class ExpenseForm(FlaskForm):
    title = StringField("Title", validators = [InputRequired()])
    type = SelectField('Type', choices=[
        ('Food', 'Food'), 
        ('Loans', 'Loans'),
        ('Housing/Rent expenses', 'Housing/Rent expenses'), 
        ('Media and communication', 'Media and communication'),  
        ('Travel and vacations', 'Travel and vacations'),
        ('Donations and gifts', 'Donations and gifts'),
        ('Entertainment and hobbies', 'Entertainment and hobbies'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other')
        ]
    )

    amount = FloatField(
        "Amount",
        validators=[InputRequired(),
                    NumberRange(min=0.01, message="Dont add empty expense")
        ]
    )

    submit = SubmitField("Submit Expense")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password", 
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Your passsword must be between 4 and 20 characters long.")
            ])
    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            EqualTo(
                "password", message="This password did not match the one in the password field."
                )
        ]
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")