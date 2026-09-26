import sqlite3

from flask import Blueprint, render_template, request

from . import queries
from .db import get_conn

bp = Blueprint('tasks', __name__)


@bp.post('/tasks')
def create():
    title = request.form.get('title', '').strip()
    category_id = request.form.get('category_id', type=int)
    if not title:
        return "Give the task a title.", 422
    if category_id is None:
        return "Missing category.", 422
    try:
        task = queries.create_task(get_conn(), title, category_id)
    except sqlite3.IntegrityError:
        return "That category no longer exists.", 422
    return render_template('_task_item.html', task=task)
