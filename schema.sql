CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT, 
    password TEXT
    );

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    opening_hours TEXT,
    created_at TIMESTAMP
);

