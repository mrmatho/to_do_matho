import sqlite3
from pathlib import Path

import click
from flask import current_app, g

MIGRATIONS_DIR = Path(__file__).parent / 'migrations'


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def get_conn():
    if 'conn' not in g:
        g.conn = connect(current_app.config['DATABASE'])
    return g.conn


def close_conn(exception=None):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()


def migrate(conn):
    current = conn.execute('PRAGMA user_version').fetchone()[0]
    applied = []
    for script in sorted(MIGRATIONS_DIR.glob('*.sql')):
        version = int(script.name.split('_', 1)[0])
        if version <= current:
            continue
        # One transaction per migration so a failing script leaves user_version untouched.
        conn.executescript(
            f'BEGIN;\n{script.read_text()}\nPRAGMA user_version = {version};\nCOMMIT;'
        )
        applied.append(script.name)
    return applied


@click.command('init-db')
def init_db_command():
    """Create the database, or apply any pending migrations."""
    conn = connect(current_app.config['DATABASE'])
    try:
        applied = migrate(conn)
    finally:
        conn.close()
    if applied:
        click.echo(f"Applied: {', '.join(applied)}")
    else:
        click.echo("Database is up to date.")


def init_app(app):
    app.teardown_appcontext(close_conn)
    app.cli.add_command(init_db_command)
