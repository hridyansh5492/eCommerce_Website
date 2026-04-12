# routes/orders.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from ecommerce.database import get_db
from ecommerce.decorators import login_required

orders_bp = Blueprint('orders', __name__)


# ─── CHECKOUT PAGE ───────────────────────────────────────
@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))

    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        db      = get_db()
        user_id = session['user_id']

        # ── Step 1: Validate stock before placing order ──
        for pid, item in cart.items():
            product = db.execute(
                'SELECT stock FROM products WHERE id = ?', (pid,)
            ).fetchone()

            if not product or product['stock'] < item['quantity']:
                flash(
                    f"Sorry, '{item['name']}' has insufficient stock.",
                    'danger'
                )
                return redirect(url_for('cart.view_cart'))

        # ── Step 2: Create the order ──
        cursor = db.execute(
            'INSERT INTO orders (user_id, total_price, status) VALUES (?, ?, ?)',
            (user_id, total, 'pending')
        )
        order_id = cursor.lastrowid

        # ── Step 3: Insert order items + reduce stock ──
        for pid, item in cart.items():
            db.execute(
                '''INSERT INTO order_items
                   (order_id, product_id, quantity, price)
                   VALUES (?, ?, ?, ?)''',
                (order_id, int(pid), item['quantity'], item['price'])
            )
            # Reduce product stock
            db.execute(
                'UPDATE products SET stock = stock - ? WHERE id = ?',
                (item['quantity'], int(pid))
            )

        db.commit()

        # ── Step 4: Clear the cart ──
        session.pop('cart', None)

        flash(f'Order #{order_id} placed successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order_id))

    return render_template('orders/checkout.html', cart=cart, total=total)


# ─── ORDER HISTORY ───────────────────────────────────────
@orders_bp.route('/orders')
@login_required
def order_history():
    db      = get_db()
    user_id = session['user_id']

    orders = db.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()

    return render_template('orders/history.html', orders=orders)


# ─── ORDER DETAIL ────────────────────────────────────────
@orders_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    db      = get_db()
    user_id = session['user_id']

    order = db.execute(
        'SELECT * FROM orders WHERE id = ? AND user_id = ?',
        (order_id, user_id)
    ).fetchone()

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders.order_history'))

    # Get all items in this order with product names
    items = db.execute(
        '''SELECT oi.*, p.name, p.image_url
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?''',
        (order_id,)
    ).fetchall()

    return render_template('orders/detail.html', order=order, items=items)

# ─── ORDER TRACKING (visual status) ──────────────────────
@orders_bp.route('/orders/<int:order_id>/track')
@login_required
def track_order(order_id):
    db      = get_db()
    user_id = session['user_id']

    order = db.execute(
        'SELECT * FROM orders WHERE id = ? AND user_id = ?',
        (order_id, user_id)
    ).fetchone()

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders.order_history'))

    # Status pipeline — used to render progress bar
    statuses = ['pending', 'processing', 'shipped', 'delivered']
    try:
        current_step = statuses.index(order['status'])
    except ValueError:
        current_step = 0   # cancelled orders

    return render_template('orders/tracking.html',
                            order        = order,
                            statuses     = statuses,
                            current_step = current_step)


# ─── RECOMMENDATIONS ─────────────────────────────────────
@orders_bp.route('/recommendations')
@login_required
def recommendations():
    db      = get_db()
    user_id = session['user_id']

    # Strategy 1: categories the user has ordered before
    ordered_categories = db.execute(
        '''SELECT DISTINCT p.category
            FROM order_items oi
            JOIN orders o  ON o.id  = oi.order_id
            JOIN products p ON p.id = oi.product_id
            WHERE o.user_id = ?''',
        (user_id,)
    ).fetchall()

    # Strategy 2: products NOT yet ordered by this user,
    #             in those same categories
    recommended = []
    if ordered_categories:
        cats        = [r['category'] for r in ordered_categories]
        placeholders = ','.join('?' * len(cats))

        recommended = db.execute(
            f'''SELECT * FROM products
                WHERE category IN ({placeholders})
                    AND stock > 0
                    AND id NOT IN (
                        SELECT oi.product_id
                        FROM order_items oi
                        JOIN orders o ON o.id = oi.order_id
                        WHERE o.user_id = ?
                    )
                ORDER BY RANDOM() LIMIT 8''',
            (*cats, user_id)
        ).fetchall()

    # Strategy 3: fallback — popular products if no history
    if not recommended:
        recommended = db.execute(
            '''SELECT p.* FROM products p
                JOIN order_items oi ON oi.product_id = p.id
                WHERE p.stock > 0
                GROUP BY p.id
                ORDER BY SUM(oi.quantity) DESC LIMIT 8'''
        ).fetchall()

    return render_template('orders/recommendations.html',
                            recommended = recommended,
                            has_history = bool(ordered_categories))