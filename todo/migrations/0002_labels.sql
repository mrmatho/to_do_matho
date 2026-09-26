CREATE TABLE labels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE CHECK (length(name) > 0),
    kind TEXT NOT NULL CHECK (kind IN ('tag', 'context')),
    UNIQUE (kind, name)
);

CREATE TABLE task_labels (
    task_id INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    label_id INTEGER NOT NULL REFERENCES labels (id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, label_id)
);
