import json


def categories(conn):
    return conn.execute('SELECT * FROM categories ORDER BY position').fetchall()


def board(conn):
    all_categories = categories(conn)
    tasks_by_category = {category['id']: [] for category in all_categories}
    tasks = _with_labels(conn, conn.execute('SELECT * FROM tasks ORDER BY position').fetchall())
    for task in tasks:
        tasks_by_category[task['category_id']].append(task)
    return [(category, tasks_by_category[category['id']]) for category in all_categories]


def get_task(conn, task_id):
    rows = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchall()
    return _with_labels(conn, rows)[0] if rows else None


def _with_labels(conn, tasks):
    labels = {}
    for row in conn.execute(
        '''
        SELECT tl.task_id, l.kind, l.name
        FROM task_labels tl JOIN labels l ON l.id = tl.label_id
        WHERE tl.task_id IN (SELECT value FROM json_each(?))
        ORDER BY l.kind, l.name
        ''',
        (json.dumps([task['id'] for task in tasks]),),
    ):
        labels.setdefault(row['task_id'], []).append(row)
    return [dict(task, labels=labels.get(task['id'], [])) for task in tasks]


def create_task(conn, title, category_id):
    with conn:
        task = conn.execute(
            '''
            INSERT INTO tasks (title, category_id, position)
            VALUES (?, ?, (SELECT coalesce(max(position) + 1, 0) FROM tasks WHERE category_id = ?))
            RETURNING *
            ''',
            (title, category_id, category_id),
        ).fetchone()
    return dict(task, labels=[])


def update_task(conn, task_id, *, title, notes, category_id, completed, labels):
    """`labels` is an iterable of (kind, name). Returns False if the task doesn't exist."""
    with conn:
        task = conn.execute('SELECT category_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if task is None:
            return False
        conn.execute(
            '''
            UPDATE tasks
            SET title = ?, notes = ?,
                completed_at = CASE WHEN ? THEN coalesce(completed_at, CURRENT_TIMESTAMP) END
            WHERE id = ?
            ''',
            (title, notes, completed, task_id),
        )
        if category_id != task['category_id']:
            conn.execute(
                '''
                UPDATE tasks
                SET category_id = ?,
                    position = (SELECT coalesce(max(position) + 1, 0) FROM tasks WHERE category_id = ?)
                WHERE id = ?
                ''',
                (category_id, category_id, task_id),
            )
            _renumber(conn, task['category_id'])
        conn.execute('DELETE FROM task_labels WHERE task_id = ?', (task_id,))
        for kind, name in labels:
            conn.execute(
                'INSERT INTO labels (kind, name) VALUES (?, ?) ON CONFLICT (kind, name) DO NOTHING',
                (kind, name),
            )
            conn.execute(
                '''
                INSERT OR IGNORE INTO task_labels (task_id, label_id)
                SELECT ?, id FROM labels WHERE kind = ? AND name = ?
                ''',
                (task_id, kind, name),
            )
        _delete_unused_labels(conn)
    return True


def delete_task(conn, task_id):
    """Returns False if the task doesn't exist."""
    with conn:
        task = conn.execute(
            'DELETE FROM tasks WHERE id = ? RETURNING category_id', (task_id,)
        ).fetchone()
        if task is None:
            return False
        _renumber(conn, task['category_id'])
        _delete_unused_labels(conn)
    return True


def _delete_unused_labels(conn):
    conn.execute('DELETE FROM labels WHERE id NOT IN (SELECT label_id FROM task_labels)')


def move_task(conn, task_id, category_id, position):
    """Move a task to `position` within `category_id`. Returns False if the task doesn't exist."""
    with conn:
        task = conn.execute('SELECT category_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if task is None:
            return False
        ids = [
            row['id']
            for row in conn.execute(
                'SELECT id FROM tasks WHERE category_id = ? AND id != ? ORDER BY position',
                (category_id, task_id),
            )
        ]
        ids.insert(min(position, len(ids)), task_id)
        conn.executemany(
            'UPDATE tasks SET category_id = ?, position = ? WHERE id = ?',
            [(category_id, index, id_) for index, id_ in enumerate(ids)],
        )
        if task['category_id'] != category_id:
            _renumber(conn, task['category_id'])
    return True


def _renumber(conn, category_id):
    ids = conn.execute(
        'SELECT id FROM tasks WHERE category_id = ? ORDER BY position', (category_id,)
    ).fetchall()
    conn.executemany(
        'UPDATE tasks SET position = ? WHERE id = ?',
        [(index, row['id']) for index, row in enumerate(ids)],
    )


def create_category(conn, name, color):
    with conn:
        return conn.execute(
            '''
            INSERT INTO categories (name, color, position)
            VALUES (?, ?, (SELECT coalesce(max(position) + 1, 0) FROM categories))
            RETURNING *
            ''',
            (name, color),
        ).fetchone()
