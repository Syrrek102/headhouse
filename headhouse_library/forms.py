from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, TextAreaField, URLField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo

class BudgetForm(FlaskForm):
    amount = FloatField(
        "Amount",
        validators=[InputRequired(),
                    NumberRange(min=0.01, message="Dont add empty expense")
        ]
    )

    submit = SubmitField("Set Budget")


class ExpenseForm(FlaskForm):
    title = StringField("Title", validators = [InputRequired()])
    type = StringField("Type", validators = [InputRequired()])

    amount = FloatField(
        "Amount",
        validators=[InputRequired(),
                    NumberRange(min=0.01, message="Dont add empty expense")
        ]
    )

    submit = SubmitField("Add Expense")
