from flask import Flask, render_template, url_for, request, flash, redirect, session
import pymysql
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# db_host = "10.1.10.247"
# db_port = 3306
# db_user = "fakubri"
# db_password = "my_secret_password"
# db_database = "fakubri"


def connection():
    s = '10.1.10.247'
    d = 'fakubri'
    u = 'fakubri'
    p = 'my_secret_password'
    con = pymysql.connect(
        host=s,
        user=u,
        password=p,
        database=d,
        autocommit=True)
    return con


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ahgi2Soh1foo6oodeeHei8ooquohth5aeKaghooH'
date_now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")


@app.route('/')
def index():
    return render_template("index.html", active_menu='index')


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", username=session['username'], active_menu='dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        _username = request.form['username']
        _password = request.form['password']

        # connect to mysql
        con = connection()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s AND deleted=0', (_username,))
        data = cursor.fetchall()
        is_active = data[0][5]
        is_admin = data[0][8]
        # print(f"Active: {data[0][5]}")
        if len(data) > 0:
            if is_active == 0:
                flash("Account is not activated. Contact with your administrator")
                return render_template('error.html', active_menu='login')
            if check_password_hash(str(data[0][4]), _password):
                session['loggedin'] = True
                session['user'] = data[0][0]
                session['username'] = data[0][1]
                # print(data)
                return redirect(url_for('dashboard', is_admin=is_admin))
            else:
                flash("Wrong username/password.")
                return render_template('error.html', active_menu='login')
        else:
            flash("Wrong login or Password.")
            return render_template('error.html', active_menu='login')
    except Exception as e:
        # return render_template('error.html', error=str(e))
        return render_template('error.html', error=str(e))


# dzialajacy (obecny)
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         con = connection()
#         cursor = con.cursor()
#         cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
#         record = cursor.fetchone()
#         if record:
#             session['loggedin'] = True
#             session['username'] = record[1]
#             con.close()
#             return redirect(url_for('dashboard'))
#         else:
#             msg = 'Incorrect username/password. Try again!'
#     return render_template('index.html', msg=msg, active_menu='login')


# dzialajacy
@app.route('/logout')
def logout():
    flash("Successfully logged out!")
    session.pop('loggedin', None)
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('index'))


############################


@app.route('/users')
def users():
    users = []
    con = connection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        if row[4]:
            users.append({"id": row[0],
                          "username": row[1],
                          "first_name": row[2],
                          "last_name": row[3],
                          "password": row[4],
                          "active": row[5],
                          "date_joined": row[6],
                          "deleted": row[7],
                          "is_admin": row[8]})
    con.close()
    return render_template("users.html", users=users, active_menu='users')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", user={}, active_menu='register')
    if request.method == 'POST':
        # id = int(request.form["id"])
        # name = request.form["name"]
        # year = int(request.form["year"])
        # price = float(request.form["price"])
        username = str(request.form['username'])
        first_name = str(request.form['first_name'])
        last_name = str(request.form['last_name'])
        password = generate_password_hash(request.form['password'])
        con = connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO users (username, first_name, last_name, password, date_joined) VALUES (%s, %s, %s, %s, %s)", (username, first_name, last_name, password, date_now))
        con.commit()
        return redirect(url_for('login'))


@app.route('/delete/<int:id>')
def delete_user(id):
    con = connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id))
    con.commit()
    con.close()
    return redirect(url_for('users'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    update_user = []
    con = connection()
    cursor = con.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM users WHERE id = %s", (id))
        for row in cursor.fetchall():
            update_user.append({"username": row[1],
                                "first_name": row[2],
                                "last_name": row[3],
                                "password": row[4],
                                "active": row[5],
                                "deleted": row[7]})
        con.close()
        return render_template("edit_user.html", user=update_user[0])
    if request.method == 'POST':
        username = str(request.form['username'])
        first_name = str(request.form['first_name'])
        last_name = str(request.form['last_name'])
        active = str(request.form['active'])
        deleted = str(request.form['deleted'])
        cursor.execute("UPDATE users SET username=%s, first_name=%s, last_name=%s, active=%s, deleted=%s WHERE id = %s", (username, first_name, last_name, active, deleted, id))
        con.commit()
        con.close()
        return redirect(url_for('users'))


# Działający register - nie usuwać!
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     db = pymysql.connect(host=db_host,
#                         user=db_user,
#                         password=db_password,
#                         database=db_database,
#                         charset='utf8mb4',
#                         cursorclass=pymysql.cursors.DictCursor)
#     if request.method == 'GET':
#         return render_template('register.html', active_menu='register')
#     else:
#         username = 'admin'
#         if 'username' in request.form:
#             username = request.form['username']
#         password = 'admin'
#         if 'password' in request.form:
#             password = request.form['password']

#         with db:
#             with db.cursor() as cursor:
#                 sql = "INSERT INTO `users` (`username`, `password`, `date_joined`) VALUES (%s, %s, %s)"
#                 cursor.execute(sql, (username, password, date_now))
#             db.commit()
#             return redirect(url_for('users'))
#             # return render_template('register_results.html', username=username, password=password, active_menu='register')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html', active_menu='login')
#     else:
#         username = '' if 'username' not in request.form else request.form['username']
#         password = '' if 'password' not in request.form else request.form['password']

#         user_login = UserPass(username, password)
#         user_record = user_login.login_user()

#         if user_record is not None:
#             session['user'] = username
#             flash('Sign in successfull, Welcome {}'.format(username))
#             return redirect(url_for('index'))
#         else:
#             flash('Sign in failed, try again')
#             return render_template('login.html', active_menu='login')


# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         con = connection()
#         cursor = con.cursor()
#         cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
#         account = cursor.fetchone()
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             return redirect(url_for('home'))
#         else:
#             flash("Incorrect username/password!", "danger")
#             return render_template('login.html', active_menu='login')
#     return render_template('login.html', title="Login")


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    db = pymysql.connect(host=db_host,
                        port=db_port,
                        user=db_user,
                        password=db_password,
                        database=db_database,
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
    if request.method == 'GET':
        return render_template('users.html', active_menu='users')
    else:
        id = '' if 'id' not in request.form else request.form['id']
        username = 'admin'
        if 'username' in request.form:
            username = request.form['username']
        password = 'admin'
        if 'password' in request.form:
            password = request.form['password']

        with db:
            with db.cursor() as cursor:
                sql = "DELETE FROM `users` WHERE id=%s"
                cursor.execute(sql, (username, password, date_now))
            db.commit()
            # return redirect(url_for('users'))
            return render_template('delete_results.html', id=id, username=username, password=password, active_menu='users')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
