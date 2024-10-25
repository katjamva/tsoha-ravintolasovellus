CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT,
    role TEXT
    );

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    address TEXT,
    created_at TIMESTAMP
);


CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    stars INTEGER,
    comment TEXT
);

CREATE TABLE openinghours (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    day INTEGER,
    opening TEXT,
    closing TEXT
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories(
    id SERIAL PRIMARY KEY,
    category TEXT UNIQUE NOT NULL
);


CREATE TABLE restaurant_categories(
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, category_id)
);
