import re
import sqlite3

from flask import Blueprint, render_template, request

from . import queries
from .board import render_board
from .db import get_conn

bp = Blueprint('tasks', __name__)


def parse_labels(text):
    """'@home #errand shopping' -> [('context', 'home'), ('tag', 'errand'), ('tag', 'shopping')]"""
    labels = {}
    for token in re.split(r'[\s,]+', text):
        name = token.lstrip('@#')
        if name:
            kind = 'context' if token.startswith('@') else 'tag'
            labels.setdefault((kind, name.casefold()), (kind, name))
    return list(labels.values())


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


@bp.post('/tasks/<int:task_id>/move')
def move(task_id):
    category_id = request.form.get('category_id', type=int)
    position = request.form.get('position', type=int)
    if category_id is None or position is None or position < 0:
        return "Invalid move.", 422
    try:
        moved = queries.move_task(get_conn(), task_id, category_id, position)
    except sqlite3.IntegrityError:
        return "That category no longer exists.", 422
    if not moved:
        return "That task no longer exists.", 404
    return '', 204


@bp.get('/tasks/<int:task_id>/edit')
def edit(task_id):
    conn = get_conn()
    task = queries.get_task(conn, task_id)
    if task is None:
        return "That task no longer exists.", 404
    return render_template('_task_editor.html', task=task, categories=queries.categories(conn))


@bp.put('/tasks/<int:task_id>')
def update(task_id):
    title = request.form.get('title', '').strip()
    category_id = request.form.get('category_id', type=int)
    if not title:
        return "Give the task a title.", 422
    if category_id is None:
        return "Pick a category.", 422
    try:
        updated = queries.update_task(
            get_conn(),
            task_id,
            title=title,
            notes=request.form.get('notes', '').strip(),
            category_id=category_id,
            completed='completed' in request.form,
            labels=parse_labels(request.form.get('labels', '')),
        )
    except sqlite3.IntegrityError:
        return "That category no longer exists.", 422
    if not updated:
        return "That task no longer exists.", 404
    return render_board()


@bp.delete('/tasks/<int:task_id>')
def delete(task_id):
    if not queries.delete_task(get_conn(), task_id):
        return "That task no longer exists.", 404
    return render_board()
