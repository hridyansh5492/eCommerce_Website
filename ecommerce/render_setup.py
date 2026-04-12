# render_setup.py
import os
import sqlite3

DB_PATH = os.path.join('instance', 'ecommerce.db')
os.makedirs('instance', exist_ok=True)

def setup():
    # Only initialize if DB doesn't exist yet
    if os.path.exists(DB_PATH):
        print("Database already exists, skipping setup.")
        return

    print("Initializing database...")
    db = sqlite3.connect(DB_PATH)

    with open('schema.sql', 'r') as f:
        db.executescript(f.read())

    # Insert sample products
    products = [
        ('Wireless Headphones', 'Noise-cancelling headphones.', 2999.00, 25,
        'Electronics',
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
        ('Running Shoes', 'Lightweight running shoes.', 1499.00, 40,
        'Footwear',
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
        ('Python Book', 'Learn Python from scratch.', 599.00, 60,
        'Books',
        'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'),
        ('LED Desk Lamp', 'Adjustable brightness lamp.', 899.00, 30,
        'Home',
        'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400'),
        ('Laptop Backpack', 'Water-resistant 30L backpack.', 1199.00, 20,
        'Accessories',
        'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'),
        ('Mechanical Keyboard', 'RGB mechanical keyboard.', 3499.00, 15,
        'Electronics',
        'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400'),
    ]

    db.executemany(
        '''INSERT INTO products
            (name, description, price, stock, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?)''',
        products
    )
    db.commit()
    db.close()
    print("Database ready with sample data.")

if __name__ == '__main__':
    setup()