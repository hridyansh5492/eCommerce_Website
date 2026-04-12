-- Drop tables if they exist (useful during development)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- 1. USERS table
CREATE TABLE users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT NOT NULL UNIQUE,
    email        TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role         TEXT NOT NULL DEFAULT 'customer',  -- 'customer' or 'admin'
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. PRODUCTS table
CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    price       REAL NOT NULL,
    stock       INTEGER NOT NULL DEFAULT 0,
    category    TEXT,
    image_url   TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. ORDERS table
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    total_price REAL NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    -- status values: pending, processing, shipped, delivered, cancelled
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. ORDER_ITEMS table (links orders to products)
CREATE TABLE order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL,
    price      REAL NOT NULL,   -- price at time of purchase (important!)
    FOREIGN KEY (order_id)   REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);