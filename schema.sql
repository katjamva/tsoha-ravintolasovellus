CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE CONSTRAINT, 
    password TEXT,
    role TEXT
    );

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    opening_hours TEXT,
    created_at TIMESTAMP,
    cuisine TEXT
);


CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    restaurant_id INTEGER REFERENCES restaurants,
    stars INTEGER,
    comment TEXT
);
