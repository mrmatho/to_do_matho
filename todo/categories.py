import re
import sqlite3

from flask import Blueprint, render_template, request

from . import queries
from .db import get_conn

bp = Blueprint('categories', __name__)

HEX_COLOR = re.compile(r'#[0-9a-fA-F]{6}')


@bp.post('/categories')
def create():
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#ffffff')
    if not name:
        return "Give the category a name.", 422
    if not HEX_COLOR.fullmatch(color):
        return "Pick a colour.", 422
    try:
        category = queries.create_category(get_conn(), name, color)
    except sqlite3.IntegrityError:
        return "A category with that name already exists.", 409
    return render_template('_category_column.html', category=category, tasks=[])
