from decimal import Decimal

import datetime
import sqlite3
from flask import Flask, request, render_template, session, redirect, abort, url_for
from unicodedata import category
from datetime import datetime

import database
import models
from sqlalchemy import select
from database import db_session, init_db

app = Flask(__name__)
app.secret_key = 'lkjihasdfnmcx'

SPEND = 1
INCOME = 2

#tews
@app.route('/', methods=['GET'])
def main_page():
    if 'user_id' not in session:
        return redirect('/login')

    init_db()

    start_s = request.args.get('start')
    end_s   = request.args.get('end')

    def parse_date(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, '%Y-%m-%d').date()
        except ValueError:
            return None

    start_date = parse_date(start_s)
    end_date   = parse_date(end_s)
    if start_date and end_date and start_date > end_date:
        start_date, end_date = end_date, start_date
        start_s, end_s = end_s, start_s

    stmt = select(models.Transaction).filter_by(owner=session['user_id'])
    if start_date:
        stmt = stmt.where(models.Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(models.Transaction.date <= end_date)
    stmt = stmt.order_by(models.Transaction.date.desc(), models.Transaction.id.desc())

    user_transactions = db_session.execute(stmt).scalars().all()

    user = db_session.get(models.User, session['user_id'])
    categories = db_session.execute(select(models.Category)).scalars().all()
    cat_by_id = {c.id: c.name for c in categories}

    def to_dec(x):
        return Decimal(str(x)) if x is not None else Decimal('0')
    def tcode(v):
        try:
            return int(v)
        except Exception:
            return v

    total_income  = sum(to_dec(t.amount) for t in user_transactions if tcode(t.type) == 2)  # 2 = Income
    total_expense = sum(to_dec(t.amount) for t in user_transactions if tcode(t.type) == 1)  # 1 = Expense

    return render_template(
        "main_page.html",
        user=user,
        user_transactions=user_transactions,
        cat_by_id=cat_by_id,
        total_income=total_income,
        total_expense=total_expense,
        start=start_s,
        end=end_s
    )


@app.route('/user', methods=['GET', 'DELETE'])
def user_handler():
    if request.method == 'GET':
        return 'Hello World! GET'
    else:
        return 'Hello World DELETE'


@app.route('/login', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        init_db()
        data = list(db_session.execute(select(models.User).filter_by(email=email, password=password)).scalars())
        if data:
            session['user_id'] = data[0].id
            return "You have been successfully logined "
        else:
            return "Wrong email or password"


@app.route('/logout', methods=['GET'])
def logout_handler():
    session.clear()
    return redirect("login")


@app.route('/register', methods=['GET', 'POST'])
def register_handler():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        email = request.form['email']
        init_db()
        new_user = models.User(name=name, surname=surname, password=password, email=email)
        database.db_session.add(new_user)
        database.db_session.commit()
        return f'User, {name}, was registered'


@app.route('/category', methods=['GET', 'POST'])
def get_all_category123():
    if 'user_id' in session:
        if request.method == 'GET':
            init_db()
            categories = list(db_session.execute(select(models.Category).filter_by(owner=session['user_id'])).scalars())
            categories_system = list(db_session.execute(select(models.Category).filter_by(owner=1)).scalars())
            return render_template("all_categories.html", categories=categories + categories_system)
        else:
            category_name = request.form['category_name']
            category_owner = session['user_id']
            init_db()

            new_category = models.Category(name=category_name, owner=category_owner)
            database.db_session.add(new_category)
            database.db_session.commit()
            return redirect('/category')
    else:
        return redirect('/login')


@app.route("/category/<category_id>", methods=["GET"])
def get_category(category_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Category).filter_by(
            owner=session["user_id"], id=category_id
        )
        result = db_session.execute(stmt).scalars().first()
        return render_template("one_category.html", one_category=result)


@app.route('/category/<category_id>/edit', methods=['POST'])
def edit_category(category_id):
    if 'user_id' in session:
        init_db()
        category_name = request.form["category_name"]
        stmt = select(models.Category).filter_by(owner=session["user_id"], id=category_id)
        result = db_session.execute(stmt).scalars().first()
        result.name = category_name
        db_session.commit()
        return redirect(f"/category/{category_id}")
    else:
        return redirect("/login")


@app.route('/income', methods=['GET', 'POST'])
def get_all_income123():
    if 'user_id' in session:
        init_db()
        if request.method == 'GET':
            res = list(db_session.execute(
                select(models.Transaction).filter_by(owner=session['user_id'], type=INCOME)).scalars().all())

            categories_system = list(db_session.execute(
                select(models.Category).filter_by(owner=1)).scalars().all())

            categories_user = list(db_session.execute(
                select(models.Category).filter_by(owner=session['user_id'])).scalars().all())

            return render_template("dashboard-incomes.html", transactions=res, categories_system = categories_system, categories_user=categories_user)
        else:
            transaction_description = request.form['description']
            transaction_owner = session['user_id']
            transaction_amount = request.form['amount']
            transaction_category = request.form['category']
            transaction_type = INCOME
            transaction_date = request.form['date']

            new_transaction = models.Transaction(description=transaction_description, owner=transaction_owner,
                                                 amount=transaction_amount, category=transaction_category,
                                                 type=transaction_type, date=transaction_date)
            database.db_session.add(new_transaction)
            database.db_session.commit()

            return redirect('/income')

    else:
        return redirect('/login')

@app.route('/income/<income_id>/delete', methods=['POST'])
def delete_income(income_id):
    if 'user_id' not in session:
        return redirect('/login')

    init_db()
    tx = db_session.get(models.Transaction, income_id)
    if not tx or tx.owner != session['user_id'] or tx.type != INCOME:
        abort(404)

    db_session.delete(tx)
    db_session.commit()
    return redirect('/income')

@app.route('/spend/<spend_id>/delete', methods=['POST'])
def delete_spend(spend_id):
    if 'user_id' not in session:
        return redirect('/login')

    init_db()
    tx = db_session.get(models.Transaction, spend_id)
    if not tx or tx.owner != session['user_id'] or tx.type != SPEND:
        abort(404)

    db_session.delete(tx)
    db_session.commit()
    return redirect('/spend')

@app.route('/category/<category_id>/delete', methods=['POST'])
def delete_category(category_id):
    if 'user_id' not in session:
        return redirect('/login')

    init_db()
    cat = db_session.get(models.Category, category_id)
    if not cat or cat.owner != session['user_id'] :
        abort(404)

    db_session.delete(cat)
    db_session.commit()
    return redirect('/category')

@app.route('/income/<income_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_all_income(income_id):
    if request.method == 'GET':
        return f"Hello World! GET, {income_id}"
    elif request.method == 'PATCH':
        return f"Hello World! PATCH, {income_id}"
    else:
        return f"Hello World! DELETE, {income_id}"


@app.route('/spend', methods=['GET', 'POST'])
def get_all_spend():
    if 'user_id' in session:
        init_db()
        if request.method == 'GET':
            res = list(db_session.execute(
                select(models.Transaction).filter_by(owner=session['user_id'], type=SPEND)).scalars().all())

            categories_system= list(db_session.execute(
                select(models.Category).filter_by(owner=1)).scalars().all())

            categories_user = list(db_session.execute(
                select(models.Category).filter_by(owner=session['user_id'])).scalars().all())

            return render_template("dashboard-spend.html", transactions=res,categories_system=categories_system, categories_user=categories_user)
        else:
            transaction_description = request.form['description']
            transaction_owner = session['user_id']
            transaction_amount = request.form['amount']
            transaction_category = request.form['category']
            transaction_type = SPEND
            transaction_date = request.form['date']

            new_transaction = models.Transaction(description=transaction_description, owner=transaction_owner,
                                                 amount=transaction_amount, category=transaction_category,
                                                 type=transaction_type, date=transaction_date)
            database.db_session.add(new_transaction)
            database.db_session.commit()
            return redirect('/spend')

    else:
        return redirect('/login')


@app.route('/spend/<spend_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_spend(spend_id):
    if request.method == 'GET':
        return f"Hello World! GET, {spend_id}"
    elif request.method == 'PATCH':
        return f"Hello World! PATCH, {spend_id}"
    else:
        return f"Hello World! DELETE, {spend_id}"


if __name__ == '__main__':
    app.run()
