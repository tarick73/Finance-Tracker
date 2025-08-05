import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)


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
            result = cursor.execute(f"Select * from user where email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
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
    if request.method == 'GET':
        return 'Hello World! GET'
    else:
        return 'Hello World POST'


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
