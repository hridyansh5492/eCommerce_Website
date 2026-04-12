# seed.py
import sqlite3
import os

DB_PATH = os.path.join('instance', 'ecommerce.db')

if not os.path.exists(DB_PATH):
    print("ERROR: Database not found.")
    print("Run 'flask init-db' first, then run this script.")
    exit(1)

db = sqlite3.connect(DB_PATH)

# Check if products already exist
existing = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
if existing > 0:
    print(f"Database already has {existing} products. Skipping seed.")
    print("To re-seed: run 'flask init-db' first to reset, then run seed.py again.")
    db.close()
    exit(0)

products = [
    (
        'Wireless Headphones',
        'High-quality noise-cancelling headphones with 30hr battery life.',
        2999.00, 25, 'Electronics',
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'
    ),
    (
        'Running Shoes',
        'Lightweight mesh shoes for daily running and gym workouts.',
        1499.00, 40, 'Footwear',
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'
    ),
    (
        'Python Programming Book',
        'Learn Python from scratch. Perfect for college students.',
        599.00, 60, 'Books',
        'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'
    ),
    (
        'LED Desk Lamp',
        'Adjustable brightness LED lamp. USB charging port included.',
        899.00, 30, 'Home',
        'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400'
    ),
    (
        'Laptop Backpack',
        '30L water-resistant backpack. Fits 15.6 inch laptops.',
        1199.00, 20, 'Accessories',
        'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'
    ),
    (
        'Mechanical Keyboard',
        'RGB mechanical keyboard with blue switches. Full size layout.',
        3499.00, 15, 'Electronics',
        'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400'
    ),
    (
        'Stainless Water Bottle',
        'Keeps drinks cold 24hrs, hot 12hrs. 1 litre capacity.',
        499.00, 50, 'Accessories',
        'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400'
    ),
    (
        'Yoga Mat',
        'Non-slip 6mm thick yoga mat with carrying strap.',
        799.00, 35, 'Sports',
        'https://images.unsplash.com/photo-1601925228946-28b7e8b5df74?w=400'
    ),
]

db.executemany(
    '''INSERT INTO products
        (name, description, price, stock, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?)''',
    products
)
db.commit()
db.close()
print(f"Done! {len(products)} products inserted successfully.")