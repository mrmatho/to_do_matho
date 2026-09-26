import os

from flask import Flask

from . import board, categories, db, tasks


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['DATABASE'] = os.path.join(app.instance_path, 'todo.sqlite3')
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(board.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(tasks.bp)
    return app
