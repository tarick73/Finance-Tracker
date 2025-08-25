import sqlite3
from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)
app.secret_key = 'lkjihasdfnmcx'


SPEND = 1
INCOME = 2


class DB_class:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


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

        with DB_class('financial_tracker.db') as cursor:
            result = cursor.execute(f"Select id from user where email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
            session['user_id'] = data[0]
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
        with DB_class('financial_tracker.db') as cursor:
            cursor.execute("INSERT INTO user (name, surname, password, email) VALUES (?, ?, ?, ?)", (name,surname, password,email))
        return f'User, {name}, was registered'


@app.route('/category', methods=['GET', 'POST'])
def get_all_category123():
    if request.method == 'GET':
        return 'Hello World! GET'
    else:
        return 'Hello World POST'


@app.route('/category/<category_id>', methods=['GET', 'PATCH', 'DELETE'])
def get_all_category(category_id):
    if request.method == 'GET':
        return f"Hello World! GET, {category_id}"
    elif request.method == 'PATCH':
        return f"Hello World! PATCH, {category_id}"
    else:
        return f"Hello World! DELETE, {category_id}"


@app.route('/income', methods=['GET', 'POST'])
def get_all_income123():
    if 'user_id' in session:
        if request.method == 'GET':
            with DB_class('financial_tracker.db') as cursor:
                data = cursor.execute(f"SELECT * FROM 'transaction' where owner = {session['user_id']} and type = {INCOME}")
                res = data.fetchall()
            return render_template("dashboard.html", transactions = res)
        else:
            with DB_class('financial_tracker.db') as cursor:
                transaction_description = request.form['description']
                transaction_owner = session['user_id']
                transaction_amount = request.form['amount']
                transaction_category = request.form['category']
                transaction_type = INCOME
                transaction_date = request.form['date']
                cursor.execute(f"INSERT INTO 'transaction' (description, owner, amount, category, type, date) "
                               f"VALUES ('{transaction_description}', '{transaction_owner}','{transaction_amount}',"
                               f"'{transaction_category}','{transaction_type}','{transaction_date}') ")
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
    if request.method == 'GET':
        return 'Hello World! GET'
    else:
        return 'Hello World POST'


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
