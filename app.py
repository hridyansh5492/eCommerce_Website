# app.py
import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['DATABASE']   = os.path.join(app.instance_path, 'ecommerce.db')

    os.makedirs(app.instance_path, exist_ok=True)

    from database import init_app
    init_app(app)

    from routes.auth     import auth_bp
    from routes.products import products_bp
    from routes.cart     import cart_bp
    from routes.orders   import orders_bp
    from routes.admin    import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def home():
        from database import get_db
        db       = get_db()
        products = db.execute(
            'SELECT * FROM products WHERE stock > 0 LIMIT 8'
        ).fetchall()
        return render_template('home.html', products=products)

    @app.cli.command('init-db')
    def init_db_command():
        from database import init_db
        init_db()
        print('Database initialized.')

    return app

# Run render_setup before creating app (only in production)
if os.environ.get('RENDER'):
    from render_setup import setup
    setup()

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)