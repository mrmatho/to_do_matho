def board(conn):
    categories = conn.execute('SELECT * FROM categories ORDER BY position').fetchall()
    tasks_by_category = {category['id']: [] for category in categories}
    for task in conn.execute('SELECT * FROM tasks ORDER BY position'):
        tasks_by_category[task['category_id']].append(task)
    return [(category, tasks_by_category[category['id']]) for category in categories]


def create_task(conn, title, category_id):
    with conn:
        return conn.execute(
            '''
            INSERT INTO tasks (title, category_id, position)
            VALUES (?, ?, (SELECT coalesce(max(position) + 1, 0) FROM tasks WHERE category_id = ?))
            RETURNING *
            ''',
            (title, category_id, category_id),
        ).fetchone()


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
