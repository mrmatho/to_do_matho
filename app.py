import sqlite3
from logging import getLogger

from flask import Flask, g, render_template, request

app = Flask('todo')

DATABASE = 'todo.sqlite3'
logger = getLogger(__name__)


def get_conn():
    if 'conn' not in g:
        g.conn = sqlite3.connect(DATABASE)
        g.conn.row_factory = sqlite3.Row
    return g.conn


@app.teardown_appcontext
def close_conn(exception=None):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()

@app.route('/')
def main():
    logger.info("Rendering main page")
    tasks = get_conn().execute('SELECT * FROM tasks ORDER BY id').fetchall()
    return render_template('index.html', message="Hi", tasks=tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.form['title'].strip()
    conn = get_conn()
    cursor = conn.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
    conn.commit()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (cursor.lastrowid,)).fetchone()
    return render_template('_task_item.html', task=task)

def init_db():
    print("Initializing database...")
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#FFFFFF'
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")
    


if __name__ == '__main__':
    init_db()
    app.run(debug=True)