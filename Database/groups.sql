CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    admin_username VARCHAR(80) NOT NULL
);
