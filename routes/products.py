# routes/products.py
from flask import Blueprint, render_template, request
from database import get_db

products_bp = Blueprint('products', __name__)


# ─── ALL PRODUCTS ────────────────────────────────────────
@products_bp.route('/')
@products_bp.route('/products')
def list_products():
    db       = get_db()
    category = request.args.get('category', '')  # optional filter

    if category:
        products = db.execute(
            'SELECT * FROM products WHERE category = ? AND stock > 0',
            (category,)
        ).fetchall()
    else:
        products = db.execute(
            'SELECT * FROM products WHERE stock > 0'
        ).fetchall()

    # Get all unique categories for the filter menu
    categories = db.execute(
        'SELECT DISTINCT category FROM products'
    ).fetchall()

    return render_template('products/list.html',
                            products=products,
                            categories=categories,
                            selected_category=category)


# ─── SINGLE PRODUCT DETAIL ───────────────────────────────
@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    db      = get_db()
    product = db.execute(
        'SELECT * FROM products WHERE id = ?', (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found", 404

    # Related products — same category, exclude current
    related = db.execute(
        'SELECT * FROM products WHERE category = ? AND id != ? LIMIT 4',
        (product['category'], product_id)
    ).fetchall()

    return render_template('products/detail.html',
                            product=product,
                            related=related)