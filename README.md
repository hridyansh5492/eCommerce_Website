# ShopFlask — Flask eCommerce Project

A full-featured eCommerce web application built with Flask, SQLite, and Jinja2. Includes user authentication, product browsing, cart system, order management, admin dashboard with Chart.js analytics, order tracking, and product recommendations.

---

## Tech Stack

- **Backend** — Python 3, Flask 3.0
- **Database** — SQLite (via Python's built-in `sqlite3`)
- **Frontend** — Jinja2 templates, plain CSS, vanilla JavaScript
- **Auth** — Werkzeug password hashing + Flask sessions
- **Charts** — Chart.js (CDN)
- **Deployment** — Render (free tier), Gunicorn

---

## Features

- Register / Login / Logout with hashed passwords
- Product listing with category filter
- Product detail page with related products
- Session-based cart (add, update, remove, clear)
- Checkout with stock validation
- Order history and order detail pages
- Visual order tracking (progress bar)
- Personalised product recommendations
- Admin dashboard with live Chart.js charts
- Admin — manage orders, update order status
- Admin — add and delete products

---

## Project Structure

```
ecommerce/
├── app.py                  ← Application factory + home route
├── database.py             ← DB connection helpers
├── schema.sql              ← SQL CREATE TABLE statements
├── seed.py                 ← Insert sample products locally
├── render_setup.py         ← Auto DB init for Render deployment
├── decorators.py           ← @login_required, @admin_required
├── Procfile                ← Gunicorn start command for Render
├── requirements.txt        ← Python dependencies
├── .gitignore
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← /register, /login, /logout
│   ├── products.py         ← /products, /product/<id>
│   ├── cart.py             ← /cart, /cart/add, /cart/update, /cart/remove
│   ├── orders.py           ← /checkout, /orders, /orders/<id>, /track, /recommendations
│   └── admin.py            ← /admin/* (dashboard, orders, products)
│
├── templates/
│   ├── base.html           ← Shared layout (navbar, flash messages, footer)
│   ├── home.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── products/
│   │   ├── list.html
│   │   └── detail.html
│   ├── cart/
│   │   └── cart.html
│   ├── orders/
│   │   ├── checkout.html
│   │   ├── history.html
│   │   ├── detail.html
│   │   ├── tracking.html
│   │   └── recommendations.html
│   └── admin/
│       ├── dashboard.html
│       ├── orders.html
│       ├── products.html
│       └── add_product.html
│
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/             ← placeholder.png goes here
│
└── instance/
    └── ecommerce.db        ← Auto-created, never commit this to Git
```

---

## Running Locally

### Prerequisites

- Python 3.9 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/flask-ecommerce.git
cd flask-ecommerce
```

### 2. Create and activate a virtual environment

```bash
# Create
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
flask init-db
```

This creates `instance/ecommerce.db` and all tables from `schema.sql`.

### 5. Seed sample products

```bash
python seed.py
```

This inserts 8 sample products with real images from Unsplash.

### 6. Run the development server

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

### 7. (Optional) Make yourself an admin

After registering an account, run:

```bash
python -c "
import sqlite3, os
db = sqlite3.connect(os.path.join('instance', 'ecommerce.db'))
db.execute(\"UPDATE users SET role='admin' WHERE email='your@email.com'\")
db.commit()
db.close()
print('Admin access granted!')
"
```

Then visit **http://127.0.0.1:5000/admin**

---

## Local URL Reference

| URL | Page |
|-----|------|
| `/` | Home — featured products |
| `/products` | All products with category filter |
| `/product/<id>` | Product detail + add to cart |
| `/register` | Create account |
| `/login` | Login |
| `/cart` | View / update cart |
| `/checkout` | Place order |
| `/orders` | Order history |
| `/orders/<id>` | Order detail |
| `/orders/<id>/track` | Visual order tracker |
| `/recommendations` | Personalised suggestions |
| `/admin` | Admin dashboard (admin only) |
| `/admin/orders` | Manage all orders |
| `/admin/products` | Manage products |
| `/admin/products/add` | Add new product |

---

## Deploying on Render

### Prerequisites

- GitHub account with this project pushed to a repository
- Render account — sign up free at [render.com](https://render.com)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/flask-ecommerce.git
git branch -M main
git push -u origin main
```

### Step 2 — Create a new Web Service on Render

1. Go to [render.com](https://render.com) → click **New +** → **Web Service**
2. Click **Connect GitHub** and select your repository
3. Fill in the following settings:

| Field | Value |
|-------|-------|
| Name | `flask-ecommerce` (or any name) |
| Region | Singapore (recommended for India) |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

### Step 3 — Set Environment Variables

Scroll down to **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | A strong random string e.g. `MySecret@Flask2025!` |
| `RENDER` | `true` |

### Step 4 — Deploy

Click **Create Web Service**. Render will:
1. Pull your code from GitHub
2. Install requirements
3. Start Gunicorn
4. Run `render_setup.py` which auto-creates and seeds the database

Deployment takes about 2 minutes. You'll get a live URL like:
`https://flask-ecommerce-xxxx.onrender.com`

### Step 5 — Make yourself admin on Render

In the Render dashboard → your service → **Shell** tab, run:

```bash
python -c "
import sqlite3, os
db = sqlite3.connect(os.path.join('instance', 'ecommerce.db'))
db.execute(\"UPDATE users SET role='admin' WHERE email='your@email.com'\")
db.commit()
db.close()
print('Done!')
"
```

### Important Notes for Render

- Render's free tier **spins down after 15 minutes** of inactivity. First load may take 30–60 seconds.
- The SQLite database file lives on Render's disk. It **resets on every new deploy**. For a persistent database, upgrade to Render's paid disk or migrate to PostgreSQL.
- Never commit your `instance/` folder or `.env` file to GitHub.

---

## Database Schema

```sql
users        — id, username, email, password_hash, role, created_at
products     — id, name, description, price, stock, category, image_url, created_at
orders       — id, user_id (FK), total_price, status, created_at
order_items  — id, order_id (FK), product_id (FK), quantity, price
```

Order status values: `pending` → `processing` → `shipped` → `delivered` / `cancelled`

---

## Common Issues

**Products not showing on home page**
```bash
flask init-db
python seed.py
```
Always re-seed after re-initializing the database.

**`ModuleNotFoundError`**
Make sure your virtual environment is activated before running any commands.

**`flask: command not found`**
```bash
pip install flask
# or on some systems:
python -m flask run
```

**Port already in use**
```bash
# Kill whatever is on port 5000 and restart
python app.py
```

**Admin page shows "Admin access only"**
Run the admin upgrade script from Step 7 above with your registered email.

---

## Requirements

```
flask==3.0.3
werkzeug==3.0.3
gunicorn==22.0.0
```

---

## License

This project is built for educational/PBL purposes. Free to use and modify.
