from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'expenses.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL
                    )''')
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category = request.form['category']
        amount = request.form['amount']

        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                (date, category, amount)
            )
            conn.commit()

        return redirect('/')

    with get_db_connection() as conn:
        expenses = conn.execute(
            "SELECT date, category, amount FROM expenses ORDER BY date ASC"
        ).fetchall()

        total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0

    return render_template('index.html', expenses=expenses, total=total)



@app.route('/delete_all', methods=['POST'])
def delete_all():
    with get_db_connection() as conn:
        conn.execute("DELETE FROM expenses")
        conn.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run()
