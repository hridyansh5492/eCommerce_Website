# routes/admin.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from ecommerce.database import get_db
from ecommerce.decorators import admin_required, login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─── DASHBOARD ───────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    db = get_db()

    # Summary cards
    total_users    = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_orders   = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_revenue  = db.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status != 'cancelled'"
    ).fetchone()[0]

    # Recent orders (last 10)
    recent_orders = db.execute(
        '''SELECT o.id, o.total_price, o.status, o.created_at, u.username
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC LIMIT 10'''
    ).fetchall()

    # Sales per day (last 7 days) — for Chart.js
    sales_data = db.execute(
        '''SELECT DATE(created_at) as day,
                    COUNT(*)        as order_count,
                    SUM(total_price) as revenue
            FROM orders
        WHERE created_at >= DATE('now', '-7 days')
            AND status != 'cancelled'
            GROUP BY day
            ORDER BY day'''
    ).fetchall()

    # Top 5 selling products
    top_products = db.execute(
        '''SELECT p.name,
                SUM(oi.quantity)            as total_sold,
                SUM(oi.quantity * oi.price) as revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            GROUP BY oi.product_id
            ORDER BY total_sold DESC LIMIT 5'''
    ).fetchall()

    # Sales by category
    category_sales = db.execute(
        '''SELECT p.category,
                  SUM(oi.quantity * oi.price) as revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            GROUP BY p.category
            ORDER BY revenue DESC'''
    ).fetchall()

    return render_template('admin/dashboard.html',
        total_users    = total_users,
        total_orders   = total_orders,
        total_products = total_products,
        total_revenue  = total_revenue,
        recent_orders  = recent_orders,
        sales_data     = sales_data,
        top_products   = top_products,
        category_sales = category_sales
    )


# ─── ALL ORDERS (manage) ─────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def all_orders():
    db     = get_db()
    status = request.args.get('status', '')

    if status:
        orders = db.execute(
            '''SELECT o.*, u.username FROM orders o
                JOIN users u ON u.id = o.user_id
                WHERE o.status = ?
                ORDER BY o.created_at DESC''', (status,)
        ).fetchall()
    else:
        orders = db.execute(
            '''SELECT o.*, u.username FROM orders o
                JOIN users u ON u.id = o.user_id
                ORDER BY o.created_at DESC'''
        ).fetchall()

    return render_template('admin/orders.html', orders=orders, status=status)


# ─── UPDATE ORDER STATUS ─────────────────────────────────
@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    new_status = request.form.get('status')
    valid      = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

    if new_status not in valid:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.all_orders'))

    db = get_db()
    db.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (new_status, order_id)
    )
    db.commit()
    flash(f'Order #{order_id} updated to "{new_status}".', 'success')
    return redirect(url_for('admin.all_orders'))


# ─── MANAGE PRODUCTS ─────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def manage_products():
    db       = get_db()
    products = db.execute(
        'SELECT * FROM products ORDER BY created_at DESC'
    ).fetchall()
    return render_template('admin/products.html', products=products)


# ─── ADD PRODUCT ─────────────────────────────────────────
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name        = request.form['name'].strip()
        description = request.form['description'].strip()
        price       = float(request.form['price'])
        stock       = int(request.form['stock'])
        category    = request.form['category'].strip()
        image_url   = request.form['image_url'].strip()

        db = get_db()
        db.execute(
            '''INSERT INTO products
                (name, description, price, stock, category, image_url)
                VALUES (?, ?, ?, ?, ?, ?)''',
            (name, description, price, stock, category, image_url)
        )
        db.commit()
        flash(f'Product "{name}" added!', 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/add_product.html')


# ─── DELETE PRODUCT ──────────────────────────────────────
@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.manage_products'))