import sqlite3
from flask import Flask, request, render_template, session, redirect

import database
import models
from sqlalchemy import select
from database import db_session, init_db

app = Flask(__name__)
app.secret_key = 'lkjihasdfnmcx'

SPEND = 1
INCOME = 2
#tews

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
            return render_template("dashboard-incomes.html", transactions=res)
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
            return render_template("dashboard-spend.html", transactions=res)
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
