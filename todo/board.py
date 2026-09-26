from logging import getLogger

from flask import Blueprint, render_template

from . import queries
from .db import get_conn

bp = Blueprint('board', __name__)
logger = getLogger(__name__)


@bp.route('/')
def index():
    logger.info("Rendering main page")
    return render_template('index.html', message="Hi", board=queries.board(get_conn()))
