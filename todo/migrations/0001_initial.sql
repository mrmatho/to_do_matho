CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL DEFAULT '#ffffff',
    position INTEGER NOT NULL,
    is_inbox INTEGER NOT NULL DEFAULT 0 CHECK (is_inbox IN (0, 1))
);

CREATE UNIQUE INDEX categories_single_inbox ON categories (is_inbox) WHERE is_inbox = 1;

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    notes TEXT NOT NULL DEFAULT '',
    category_id INTEGER NOT NULL REFERENCES categories (id),
    position INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE INDEX tasks_by_category ON tasks (category_id, position);

INSERT INTO categories (name, position, is_inbox) VALUES
    ('Inbox', 0, 1),
    ('Urgent', 1, 0),
    ('Important', 2, 0);
