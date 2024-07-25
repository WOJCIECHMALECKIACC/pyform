from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'some_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'mysql-service.client-apps.svc.cluster.local'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

# Initialize the database schema
with app.app_context():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    mysql.connection.commit()
    cursor.close()


@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('account.html', username=session['username'])
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insecure SQL query construction with direct string formatting
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)  # Executing the query without parameterization

        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            return redirect(url_for('account'))
        else:
            msg = 'Incorrect username/password!'
            return render_template('login.html', msg=msg)

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if account exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # If account exists, show an error message
        if account:
            msg = 'Account already exists!'
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

        cursor.close()
        
    return render_template('register.html', msg=msg)

@app.route('/account')
def account():
    if 'loggedin' in session:
        return render_template('account.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.run(debug=True)


