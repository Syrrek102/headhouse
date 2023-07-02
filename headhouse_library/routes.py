import uuid
import datetime
import functools
from flask import (
    Blueprint, 
    render_template,  
    redirect, 
    request, 
    current_app, 
    url_for,
    flash,
    session
    )
from dateutil import relativedelta
from dataclasses import asdict
from headhouse_library.models import Budget, Expense, User
from headhouse_library.forms import BudgetForm, ExpenseForm, RegisterForm, LoginForm
from passlib.hash import pbkdf2_sha256


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


def date_range(start: datetime.date):
    dates = [
        start.replace(day=1) + relativedelta.relativedelta(months=diff) for diff in range(-5, 6)
        ]
    return dates


@pages.route("/")
@login_required
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


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id = uuid.uuid4().hex,
            email = form.email.data,
            password = pbkdf2_sha256.hash(form.password.data)
        )
        
        current_app.db.user.insert_one(asdict(user))

        flash("User registered succesfully!", "succes")

        return redirect(url_for(".login"))

    return render_template("register.html", title="HeadHouse - Register", form=form)


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credantials not correct", category="danger")
            return redirect(url_for(".login"))
        
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email
            
            return redirect(url_for(".index"))

        flash("Login credantials not correct", category="danger")

    return render_template("login.html", title="HeadHouse - Login", form=form)    



@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))


@pages.route("/budget_manager")
@login_required
def budget_manager():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)
    date = request.args.get("date")

    getExpenses = current_app.db.expense.find({"date": date, "_id": {"$in": user.expenses}})
    expenses = [Expense(**expense) for expense in getExpenses]

    getBudget = current_app.db.budget.find_one({"date": date, "_id": {"$in": user.budgets}})
    budget_amount = 0
    
    if getBudget is None:
        default_budget = Budget(
            _id=uuid.uuid4().hex,
            amount=0,
            date=date
            )
        current_app.db.budget.insert_one(asdict(default_budget))
    else:
        budget_amount = getBudget["amount"]

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


# @pages.route("/budget_manager/set_budget/<date>", methods=["GET", "POST"])
# @login_required
# def set_budget(date):
#     form = BudgetForm()

#     if form.validate_on_submit():
#         budget = Budget(
#             _id= uuid.uuid4().hex,
#             amount = form.amount.data,
#             date=date
#         )
        
#         current_app.db.budget.delete_many({"date": date})
#         current_app.db.budget.insert_one(asdict(budget))
       
#         current_app.db.user.update_one(
#             {"_id": session["user_id"]}, 
#             {"$push": {"budgets": budget._id}}
#         )

#         return redirect(url_for(".budget_manager", date=date))
    
#     return render_template(
#         "set_budget.html", 
#         title="HEADHOUSE | BudgetManager - SetBudget",
#         form=form
#         )


@pages.route("/budget_manager/set_budget/<date>", methods=["GET", "POST"])
@login_required
def set_budget(date):
    form = BudgetForm()

    if form.validate_on_submit():
        budget = Budget(
            _id=uuid.uuid4().hex,
            amount=form.amount.data,
            date=date
        )

        user_id = session["user_id"]
        user = current_app.db.user.find_one({"_id": user_id})

        previous_budget = current_app.db.budget.find_one({"_id": {"$in": user["budgets"]}, "date": date})
        if previous_budget:
            current_app.db.budget.delete_many({"_id": previous_budget["_id"]})
            current_app.db.user.update_one({"_id": user_id}, {"$pull": {"budgets": previous_budget["_id"]}})

        current_app.db.budget.insert_one(asdict(budget))
        current_app.db.user.update_one(
            {"_id": user_id},
            {"$push": {"budgets": budget._id}}
        )
        flash("Budżet został zapisany.", "success")

        return redirect(url_for(".budget_manager", date=date))

    return render_template(
        "set_budget.html",
        title="HEADHOUSE | BudgetManager - SetBudget",
        form=form
    )


@pages.route("/budget_manager/add_expense/<date>", methods=["GET", "POST"])
@login_required
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
        current_app.db.user.update_one(
            {"_id": session["user_id"]}, 
            {"$push": {"expenses": expense._id}}
        )

        return redirect(url_for(".budget_manager", date=date))

    return render_template(
        "add_expense.html", 
        title="HEADHOUSE | BudgetManager - AddExpense",
        form=form
        )



@pages.route("/budget_manager/edit_expense/<date>/<expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(date, expense_id):
    expense = Expense(**current_app.db.expense.find_one({"_id": expense_id}))
    form = ExpenseForm(obj=expense)
    
    if form.validate_on_submit():
        expense.title = form.title.data
        expense.type = form.type.data
        expense.amount = form.amount.data
        expense.date=date
    
        current_app.db.expense.update_one({"_id" : expense_id}, {"$set": asdict(expense)})
        return redirect(url_for(".budget_manager", date=date, expense_id=expense._id))

    return render_template(
        "edit_expense.html",
        title="HEADHOUSE | BudgetManager - EditExpense",
        expense=expense,
        form=form,
        date=date
    )


@pages.route("/budget_manager/delete_expense/<date>/<expense_id>", methods=["GET", "POST"])
@login_required
def delete_expense(date, expense_id):
    user_id = session["user_id"]
    expense = current_app.db.expense.find_one({"_id": expense_id})

    if request.method == "POST":
        current_app.db.expense.delete_one({"_id": expense_id})
        current_app.db.user.update_one({"_id": user_id}, {"$pull": {"expenses": expense_id}})
        flash("Expense deleted successfully.", "success")
        return redirect(url_for(".budget_manager", date=date))

    return render_template(
        "delete_expense.html",
        title="HEADHOUSE | BudgetManager - DeleteExpense",
        expense=expense,
        date=date
    )


