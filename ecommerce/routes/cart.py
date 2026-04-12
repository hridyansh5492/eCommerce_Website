# routes/cart.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from ecommerce.database import get_db
from ecommerce.decorators import login_required

cart_bp = Blueprint('cart', __name__)


# ─── HELPER: get cart from session ───────────────────────
def get_cart():
    """Cart structure: { product_id: { name, price, quantity, image_url } }"""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']


# ─── VIEW CART ───────────────────────────────────────────
@cart_bp.route('/cart')
@login_required
def view_cart():
    cart  = get_cart()
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart/cart.html', cart=cart, total=total)


# ─── ADD TO CART ─────────────────────────────────────────
@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    db       = get_db()
    product  = db.execute(
        'SELECT * FROM products WHERE id = ?', (product_id,)
    ).fetchone()

    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products.list_products'))

    quantity = int(request.form.get('quantity', 1))
    cart     = get_cart()
    pid      = str(product_id)   # session keys must be strings

    if pid in cart:
        # Product already in cart — increase quantity
        new_qty = cart[pid]['quantity'] + quantity
        # Don't exceed stock
        if new_qty > product['stock']:
            flash(f"Only {product['stock']} units available.", 'warning')
            new_qty = product['stock']
        cart[pid]['quantity'] = new_qty
    else:
        cart[pid] = {
            'name':      product['name'],
            'price':     product['price'],
            'quantity':  quantity,
            'image_url': product['image_url'] or ''
        }

    session.modified = True   # tell Flask the session changed
    flash(f"'{product['name']}' added to cart!", 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))


# ─── UPDATE QUANTITY ─────────────────────────────────────
@cart_bp.route('/cart/update/<pid>', methods=['POST'])
@login_required
def update_cart(pid):
    quantity = int(request.form.get('quantity', 1))
    cart     = get_cart()

    if pid in cart:
        if quantity <= 0:
            del cart[pid]
            flash('Item removed from cart.', 'info')
        else:
            cart[pid]['quantity'] = quantity
            flash('Cart updated.', 'success')

    session.modified = True
    return redirect(url_for('cart.view_cart'))


# ─── REMOVE ITEM ─────────────────────────────────────────
@cart_bp.route('/cart/remove/<pid>', methods=['POST'])
@login_required
def remove_from_cart(pid):
    cart = get_cart()
    if pid in cart:
        removed = cart.pop(pid)
        session.modified = True
        flash(f"'{removed['name']}' removed from cart.", 'info')
    return redirect(url_for('cart.view_cart'))


# ─── CLEAR CART ──────────────────────────────────────────
@cart_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))