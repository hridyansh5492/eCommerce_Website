# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Redirect to login page if user is not logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Redirect if user is not an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Admin access only.', 'danger')
            return redirect(url_for('products.list_products'))
        return f(*args, **kwargs)
    return decorated_function