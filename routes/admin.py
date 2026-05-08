# routes/admin.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from database import get_db
from decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─── DASHBOARD ───────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    db = get_db()

    total_users    = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_orders   = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_revenue  = db.execute(
        "SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status != 'cancelled'"
    ).fetchone()[0]

    recent_orders = db.execute(
        '''SELECT o.id, o.total_price, o.status, o.created_at, u.username
            FROM orders o JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC LIMIT 10'''
    ).fetchall()

    sales_data = db.execute(
        '''SELECT DATE(created_at) as day,
                COUNT(*) as order_count,
                SUM(total_price) as revenue
            FROM orders
            WHERE created_at >= DATE('now','-7 days')
            AND status != 'cancelled'
            GROUP BY day ORDER BY day'''
    ).fetchall()

    top_products = db.execute(
        '''SELECT p.name,
                SUM(oi.quantity) as total_sold,
                  SUM(oi.quantity * oi.price) as revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            GROUP BY oi.product_id
            ORDER BY total_sold DESC LIMIT 5'''
    ).fetchall()

    category_sales = db.execute(
        '''SELECT p.category,
                  SUM(oi.quantity * oi.price) as revenue
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            GROUP BY p.category ORDER BY revenue DESC'''
    ).fetchall()

    # Safe lists for Chart.js — never pass empty
    sales_days    = [r['day']         for r in sales_data]    or ['No data']
    sales_revenue = [r['revenue']     for r in sales_data]    or [0]
    sales_orders  = [r['order_count'] for r in sales_data]    or [0]
    cat_labels    = [r['category']    for r in category_sales] or ['No data']
    cat_revenue   = [r['revenue']     for r in category_sales] or [0]

    return render_template('admin/dashboard.html',
        total_users    = total_users,
        total_orders   = total_orders,
        total_products = total_products,
        total_revenue  = total_revenue,
        recent_orders  = recent_orders,
        top_products   = top_products,
        sales_days     = sales_days,
        sales_revenue  = sales_revenue,
        sales_orders   = sales_orders,
        cat_labels     = cat_labels,
        cat_revenue    = cat_revenue,
    )


# ─── ALL ORDERS ──────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def all_orders():
    db     = get_db()
    status = request.args.get('status', '')
    if status:
        orders = db.execute(
            '''SELECT o.*, u.username FROM orders o
                JOIN users u ON u.id = o.user_id
                WHERE o.status = ? ORDER BY o.created_at DESC''', (status,)
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
    valid = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.all_orders'))
    db = get_db()
    db.execute('UPDATE orders SET status=? WHERE id=?', (new_status, order_id))
    db.commit()
    flash(f'Order #{order_id} updated to "{new_status}".', 'success')
    return redirect(url_for('admin.all_orders'))


# ─── MANAGE PRODUCTS ─────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def manage_products():
    db       = get_db()
    search   = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query  = 'SELECT * FROM products WHERE 1=1'
    params = []
    if search:
        query += ' AND name LIKE ?'
        params.append(f'%{search}%')
    if category:
        query += ' AND category = ?'
        params.append(category)
    query += ' ORDER BY created_at DESC'

    products   = db.execute(query, params).fetchall()
    categories = db.execute(
        'SELECT DISTINCT category FROM products ORDER BY category'
    ).fetchall()

    return render_template('admin/products.html',
                            products=products,
                            categories=categories,
                            search=search,
                            selected_category=category)


# ─── ADD PRODUCT ─────────────────────────────────────────
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    # Default empty form data
    form = {
        'name': '', 'description': '',
        'price': '', 'stock': '',
        'category': '', 'image_url': ''
    }

    if request.method == 'POST':
        # Pull values from form
        form['name']        = request.form.get('name', '').strip()
        form['description'] = request.form.get('description', '').strip()
        form['category']    = request.form.get('category', '').strip()
        form['image_url']   = request.form.get('image_url', '').strip()
        form['price']       = request.form.get('price', '').strip()
        form['stock']       = request.form.get('stock', '').strip()

        error = None

        if not form['name']:
            error = 'Product name is required.'
        elif not form['category']:
            error = 'Category is required.'
        elif not form['price']:
            error = 'Price is required.'
        elif not form['stock']:
            error = 'Stock is required.'
        else:
            try:
                price = float(form['price'])
                if price < 0:
                    error = 'Price cannot be negative.'
            except ValueError:
                error = 'Enter a valid price (e.g. 999.00).'

            if error is None:
                try:
                    stock = int(form['stock'])
                    if stock < 0:
                        error = 'Stock cannot be negative.'
                except ValueError:
                    error = 'Enter a valid whole number for stock.'

        if error:
            flash(error, 'danger')
            return render_template('admin/add_product.html', form=form)

        db = get_db()
        db.execute(
            '''INSERT INTO products
                (name, description, price, stock, category, image_url)
                VALUES (?, ?, ?, ?, ?, ?)''',
            (form['name'], form['description'],
            float(form['price']), int(form['stock']),
            form['category'], form['image_url'])
        )
        db.commit()
        flash(f"Product \"{form['name']}\" added successfully!", 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/add_product.html', form=form)


# ─── EDIT PRODUCT ────────────────────────────────────────
@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    db      = get_db()
    product = db.execute(
        'SELECT * FROM products WHERE id = ?', (product_id,)
    ).fetchone()

    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin.manage_products'))

    # On GET — pre-fill form with existing product data
    form = {
        'name':        product['name'],
        'description': product['description'] or '',
        'price':       product['price'],
        'stock':       product['stock'],
        'category':    product['category'],
        'image_url':   product['image_url'] or '',
    }

    if request.method == 'POST':
        form['name']        = request.form.get('name', '').strip()
        form['description'] = request.form.get('description', '').strip()
        form['category']    = request.form.get('category', '').strip()
        form['image_url']   = request.form.get('image_url', '').strip()
        form['price']       = request.form.get('price', '').strip()
        form['stock']       = request.form.get('stock', '').strip()

        error = None

        if not form['name']:
            error = 'Product name is required.'
        elif not form['category']:
            error = 'Category is required.'
        elif not form['price']:
            error = 'Price is required.'
        elif not form['stock']:
            error = 'Stock is required.'
        else:
            try:
                price = float(form['price'])
                if price < 0:
                    error = 'Price cannot be negative.'
            except ValueError:
                error = 'Enter a valid price.'

            if error is None:
                try:
                    stock = int(form['stock'])
                    if stock < 0:
                        error = 'Stock cannot be negative.'
                except ValueError:
                    error = 'Enter a valid whole number for stock.'

        if error:
            flash(error, 'danger')
            return render_template('admin/edit_product.html',
                                    form=form, product=product)

        db.execute(
            '''UPDATE products
                SET name=?, description=?, price=?, stock=?,
                category=?, image_url=?
                WHERE id=?''',
            (form['name'], form['description'],
            float(form['price']), int(form['stock']),
            form['category'], form['image_url'],
            product_id)
        )
        db.commit()
        flash(f"Product \"{form['name']}\" updated!", 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/edit_product.html',
                            form=form, product=product)


# ─── DELETE PRODUCT ──────────────────────────────────────
@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    db      = get_db()
    product = db.execute(
        'SELECT name FROM products WHERE id=?', (product_id,)
    ).fetchone()
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin.manage_products'))
    db.execute('DELETE FROM products WHERE id=?', (product_id,))
    db.commit()
    flash(f"Product \"{product['name']}\" deleted.", 'info')
    return redirect(url_for('admin.manage_products'))