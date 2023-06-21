import uuid
import datetime
import functools
from flask import (
    Blueprint, 
    render_template, 
    session, 
    redirect, 
    request, 
    current_app, 
    url_for,
    flash,
    )
from dateutil import relativedelta
from dataclasses import asdict
from headhouse_library.models import Budget, Expense
from headhouse_library.forms import BudgetForm, ExpenseForm


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def date_range(start: datetime.date):
    dates = [
        start.replace(day=1) + relativedelta.relativedelta(months=diff) for diff in range(-5, 7)
        ]
    return dates


@pages.route("/")
def index():
    date_str = request.args.get("date")

    if date_str:
        selected_date = datetime.date.fromisoformat(date_str)
    else:
        selected_date = datetime.date.today()

    return render_template(
        "index.html", 
        title="HEADHOUSE",
        date_range=date_range,
        selected_date=selected_date,
        )

@pages.route("/budget_manager")
def budget_manager():
    date = request.args.get("date")

    expense_data = current_app.db.expense.find({"date": date})
    expenses = [Expense(**expense) for expense in expense_data]


    budget_document = current_app.db.budget.find_one({"date": date})
    budget_amount = 0

    if budget_document is None:
        default_budget = Budget(_id=uuid.uuid4().hex, amount=0)
        current_app.db.budget.insert_one(asdict(default_budget))
    else:
        budget_amount = budget_document["amount"]

    total_expenses = sum(expense.amount for expense in expenses)
    budget_left = budget_amount - total_expenses


    return render_template(
        "budget_manager.html", 
        title="HEADHOUSE | BudgetManager",
        budget_amount=budget_amount,
        expenses_data=expenses,
        budget_left=budget_left,
        all_expenses=total_expenses,
        date=date
        )

@pages.route("/add_expense/<date>", methods=["GET", "POST"])
def add_expense(date):
    form = ExpenseForm()

    if form.validate_on_submit():
        expense = Expense(
            _id= uuid.uuid4().hex,
            title = form.title.data,
            type = form.type.data,
            amount = form.amount.data,
            date=date
        )

        current_app.db.expense.insert_one(asdict(expense))

        return redirect(url_for(".budget_manager", date=date))

    return render_template(
        "add_expense.html", 
        title="HEADHOUSE | BudgetManager - AddExpense",
        form=form
        )

@pages.route("/set_budget", methods=["GET", "POST"])
def set_budget():
    form = BudgetForm()

    if form.validate_on_submit():
        budget = Budget(
            _id= uuid.uuid4().hex,
            amount = form.amount.data,
        )
        
        current_app.db.budget.delete_one({})
        current_app.db.budget.insert_one(asdict(budget))

        return redirect(url_for(".budget_manager"))
    
    return render_template(
        "set_budget.html", 
        title="HEADHOUSE | BudgetManager - SetBudget",
        form=form
        )