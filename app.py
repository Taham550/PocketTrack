from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value
DB_NAME = 'expense.db'
DB_USERS = 'users.db'
def init_auth_db():
    with sqlite3.connect(DB_USERS) as conn1:
        conn1.execute('''CREATE TABLE IF NOT EXISTS users(
                      uid INTEGER PRIMARY KEY AUTOINCREMENT,
                      user TEXT NOT NULL,
                      password TEXT NOT NULL
                      
                      )''')
        conn1.commit()

def get_db_connection_auth():
    conn1 = sqlite3.connect(DB_USERS)
    conn1.row_factory = sqlite3.Row  
    return conn1

init_auth_db()

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(uid)
                    )''')
        conn.commit()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn
#quary data base
def user_exists(username,password):
    with sqlite3.connect(DB_USERS) as conn1:
        cursor = conn1.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user = ? AND password = ?", (username, password,))
        result = cursor.fetchone()
        return result[0] if result else None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        user_id = user_exists(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))
    
    return render_template("login.html")
 # register page 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']

        with get_db_connection_auth() as conn1:
            cursor = conn1.cursor()
            cursor.execute("SELECT 1 FROM users WHERE user = ?", (username,))
            if cursor.fetchone():
                return "Username already exists!"  # You can render a template with error
            cursor.execute(
                "INSERT INTO users (user, password) VALUES (?, ?)",
                (username, password)
            )
            conn1.commit()
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category = request.form['category']
        amount = request.form['amount']

        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO expenses (user_id, date, category, amount) VALUES (?, ?, ?, ?)",
                (user_id, date, category, amount)
            )
            conn.commit()

        return redirect(url_for('index'))
# quary expensses
    with get_db_connection() as conn:
        expenses = conn.execute(
            "SELECT date, category, amount FROM expenses WHERE user_id = ? ORDER BY date ASC",
            (user_id,)            
            ).fetchall()
        total = conn.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
    return render_template('index.html', expenses=expenses, total=total, username=session.get('username'))



@app.route('/delete_all', methods=['POST'])
def delete_all():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
        conn.commit()
    return redirect(url_for('index'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
