CREATE TABLE members (
    user_id TEXT,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);
