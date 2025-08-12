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

date = datetime.now().date()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
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
            "SELECT date, category, amount FROM expenses ORDER BY date DESC"
        ).fetchall()

        total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0

    return render_template('index.html', expenses=expenses, total=total)


if __name__ == '__main__':
    app.run()
