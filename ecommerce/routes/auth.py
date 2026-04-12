# routes/auth.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from ecommerce.database import get_db

auth_bp = Blueprint('auth', __name__)


# ─── REGISTER ────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        db    = get_db()
        error = None

        # Basic validation
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'

        # Check if email already exists
        if error is None:
            existing = db.execute(
                'SELECT id FROM users WHERE email = ?', (email,)
            ).fetchone()
            if existing:
                error = 'Email is already registered.'

        if error is None:
            # Hash the password — NEVER store plain text!
            hashed = generate_password_hash(password)

            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, hashed)
            )
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')


# ─── LOGIN ───────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']

        db    = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'No account found with that email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            # Save user info in session
            session.clear()
            session['user_id']   = user['id']
            session['username']  = user['username']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('products.list_products'))

        flash(error, 'danger')

    return render_template('auth/login.html')


# ─── LOGOUT ──────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))