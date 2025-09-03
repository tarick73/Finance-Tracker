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


class DB_class:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class DB_wrapper:
    def insert(self, table, data):
        with DB_class('financial_tracker.db') as cursor:
            cursor.execute(f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['?'] * len(data))})", tuple(data.values()))
    def select(self, table, params=None):
        with DB_class('financial_tracker.db') as cursor:
            if params:
                #{
                    #'id':'1',
                    #'name':'Igor',
                    #'surname':'asdas',
                    #'email':'email',
                    #
                #}
                result_params=[]
                for key, value in params.items():
                    if isinstance(value, list):
                        result_params.append(f"{key} IN {', '.join(value)}")
                    else:
                        if isinstance(value, str):
                            result_params.append(f"{key}= '{value}'")
                        else:
                            result_params.append(f"{key}= {value}")
                result_where = ' AND '.join(result_params)

                cursor.execute(f"SELECT * FROM {table} WHERE {result_where}")
            else:
                cursor.execute(f"SELECT * FROM {table}")
            return cursor.fetchall()

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
            return render_template("all_categories.html", categories=categories+categories_system)
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


@app.route('/category/<category_id>', methods=['GET', 'POST'])
def get_all_category(category_id):
    if 'user_id' in session:
        with DB_class('financial_tracker.db') as cursor:
            if request.method == 'GET':
                init_db()
                res = list(db_session.execute(select(models.Transaction).filter_by(owner=session['user_id'])).scalars())
                curr_category = list(db_session.execute(select(models.Category).filter_by(id=category_id)).scalars())

                return render_template("one_category.html", transactions=res, category=curr_category)
            else:
                return f"Hello World! DELETE, {category_id}"


@app.route('/income', methods=['GET', 'POST'])
def get_all_income123():
    if 'user_id' in session:
        init_db()
        if request.method == 'GET':
            res = list(db_session.execute(select(models.Transaction).filter_by(owner=session['user_id'], type=INCOME)).scalars().all())
            print(res)
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
        if request.method == 'GET':
            db = DB_wrapper()
            res = db.select('"transaction"', {'owner': session['user_id'], 'type': SPEND})
            return render_template("dashboard-spend.html", transactions=res)
        else:
            transaction_description = request.form['description']
            transaction_owner = session['user_id']
            transaction_amount = request.form['amount']
            transaction_category = request.form['category']
            transaction_type = SPEND
            transaction_date = request.form['date']

            db = DB_wrapper()
            db.insert('"transaction"', {'description': transaction_description, 'owner': transaction_owner, 'amount': transaction_amount, 'category': transaction_category, 'type': transaction_type, 'date': transaction_date})
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
