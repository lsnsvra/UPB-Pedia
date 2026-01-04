from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production

BASE_URL = 'https://fakestoreapi.com'

def get_all_products():
    """Fetch all products from API"""
    response = requests.get(f'{BASE_URL}/products')
    return response.json() if response.status_code == 200 else []

def get_product_by_id(product_id):
    """Fetch single product by ID"""
    response = requests.get(f'{BASE_URL}/products/{product_id}')
    return response.json() if response.status_code == 200 else None

def get_categories():
    """Fetch all categories"""
    response = requests.get(f'{BASE_URL}/products/categories')
    return response.json() if response.status_code == 200 else []

def get_cart_total_items():
    """Calculate total items in cart"""
    if 'cart' in session:
        return sum(session['cart'].values())
    return 0

@app.route('/')
def index():
    """Home page with all products"""
    # Get products
    response = requests.get(f'{BASE_URL}/products')
    products = response.json() if response.status_code == 200 else []
    
    # Apply search filter
    search_query = request.args.get('search', '')
    if search_query:
        products = [p for p in products if search_query.lower() in p['title'].lower()]
    
    # Apply category filter
    category = request.args.get('category', '')
    if category:
        products = [p for p in products if p['category'] == category]
    
    # Apply sorting
    sort_by = request.args.get('sort', '')
    if sort_by == 'price_asc':
        products.sort(key=lambda x: x['price'])
    elif sort_by == 'price_desc':
        products.sort(key=lambda x: x['price'], reverse=True)
    
    categories = get_categories()
    cart_count = get_cart_total_items()
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories,
                         cart_count=cart_count,
                         selected_category=category)

@app.route('/category/<name>')
def category(name):
    """Products by category"""
    response = requests.get(f'{BASE_URL}/products/category/{name}')
    products = response.json() if response.status_code == 200 else []
    categories = get_categories()
    cart_count = get_cart_total_items()
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories,
                         cart_count=cart_count,
                         selected_category=name)

@app.route('/product/<int:id>')
def product_detail(id):
    """Product detail page"""
    product = get_product_by_id(id)
    if not product:
        return redirect(url_for('index'))
    
    categories = get_categories()
    cart_count = get_cart_total_items()
    
    return render_template('detail.html', 
                         product=product, 
                         categories=categories,
                         cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart"""
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = {}
    
    # Get or set quantity
    quantity = int(request.form.get('quantity', 1))
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    
    session.modified = True
    
    # Redirect back to previous page
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    """Cart page"""
    cart_items = []
    total_price = 0
    
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = get_product_by_id(product_id)
            if product:
                subtotal = product['price'] * quantity
                total_price += subtotal
                cart_items.append({
                    'id': product_id,
                    'title': product['title'],
                    'price': product['price'],
                    'image': product['image'],
                    'quantity': quantity,
                    'subtotal': round(subtotal, 2)
                })
    
    categories = get_categories()
    cart_count = get_cart_total_items()
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total_price=round(total_price, 2),
                         categories=categories,
                         cart_count=cart_count)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    if 'cart' not in session:
        return redirect(url_for('cart'))
    
    # Handle remove action
    remove_id = request.form.get('remove')
    if remove_id:
        if remove_id in session['cart']:
            del session['cart'][remove_id]
    
    # Handle quantity updates for all items
    for product_id in list(session['cart'].keys()):
        quantity_key = f'quantity_{product_id}'
        if quantity_key in request.form:
            new_quantity = int(request.form[quantity_key])
            if new_quantity > 0:
                session['cart'][product_id] = new_quantity
            else:
                del session['cart'][product_id]
    
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    """Clear all items from cart"""
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))
    
    cart_items = []
    total_price = 0
    
    for product_id, quantity in session['cart'].items():
        product = get_product_by_id(product_id)
        if product:
            subtotal = product['price'] * quantity
            total_price += subtotal
            cart_items.append({
                'id': product_id,
                'title': product['title'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': round(subtotal, 2)
            })
    
    categories = get_categories()
    cart_count = get_cart_total_items()
    
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         total_price=round(total_price, 2),
                         categories=categories,
                         cart_count=cart_count)

@app.route('/complete_order', methods=['POST'])
def complete_order():
    """Simulate order completion"""
    # Clear cart after order
    session.pop('cart', None)
    
    # In a real app, you would save order to database here
    # For this demo, just redirect to index with success message
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)