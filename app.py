from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
from datetime import datetime
import json
import uuid
import traceback

app = Flask(__name__)
app.secret_key = 'tokopedia_mini_secret_key_2024'

BASE_URL = 'https://fakestoreapi.com'

# Debug mode
DEBUG = True

def debug_log(message):
    """Log debug messages"""
    if DEBUG:
        print(f"[DEBUG] {message}")

# Enhanced Payment Methods Configuration
PAYMENT_METHODS = {
    'qris': {
        'name': 'QRIS (QR Code Indonesian Standard)',
        'icon': 'fas fa-qrcode',
        'description': 'Scan QR code with any e-wallet or bank app',
        'fee': 0,
        'color': '#1e88e5',
        'supported_banks': ['All Indonesian Banks', 'E-wallets']
    },
    'dana': {
        'name': 'Dana E-Wallet',
        'icon': 'fas fa-wallet',
        'description': 'Instant payment via Dana app',
        'fee': 0,
        'color': '#00AAEE',
        'phone_number': '0812-3456-7890'
    },
    'ovo': {
        'name': 'OVO E-Wallet',
        'icon': 'fas fa-mobile-alt',
        'description': 'Pay via OVO app or QR',
        'fee': 0,
        'color': '#4F2C7F',
        'phone_number': '0812-3456-7891'
    },
    'bank_transfer': {
        'name': 'Bank Transfer',
        'icon': 'fas fa-university',
        'description': 'Manual transfer to bank account',
        'fee': 0,
        'color': '#43a047',
        'banks': [
            {'name': 'BCA', 'account': '1234567890', 'holder': 'TOKOPEDIA MINI'},
            {'name': 'Mandiri', 'account': '0987654321', 'holder': 'TOKOPEDIA STORE'},
            {'name': 'BNI', 'account': '1122334455', 'holder': 'MINI TOKOPEDIA'}
        ]
    },
    'debit_card': {
        'name': 'Debit Card',
        'icon': 'fas fa-credit-card',
        'description': 'Visa/Mastercard debit card',
        'fee': 0,
        'color': '#f39c12',
        'supported_cards': ['Visa', 'Mastercard', 'JCB']
    },
    'cod': {
        'name': 'Cash on Delivery (COD)',
        'icon': 'fas fa-money-bill-wave',
        'description': 'Pay cash when item arrives',
        'fee': 15000,
        'color': '#e74c3c',
        'max_amount': 5000000
    }
}

def get_all_products():
    """Fetch all products from API"""
    try:
        response = requests.get(f'{BASE_URL}/products', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            debug_log(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        debug_log(f"Error fetching products: {str(e)}")
        return []

def get_product_by_id(product_id):
    """Fetch single product by ID"""
    try:
        response = requests.get(f'{BASE_URL}/products/{product_id}', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            debug_log(f"API Error for product {product_id}: {response.status_code}")
            return None
    except Exception as e:
        debug_log(f"Error fetching product {product_id}: {str(e)}")
        return None

def get_categories():
    """Fetch all categories"""
    try:
        response = requests.get(f'{BASE_URL}/products/categories', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            debug_log(f"API Error categories: {response.status_code}")
            return ['electronics', 'jewelery', "men's clothing", "women's clothing"]
    except Exception as e:
        debug_log(f"Error fetching categories: {str(e)}")
        return ['electronics', 'jewelery', "men's clothing", "women's clothing"]

def initialize_cart():
    """Initialize cart in session if not exists"""
    if 'cart' not in session:
        session['cart'] = {}
        debug_log("Cart initialized")
    elif not isinstance(session['cart'], dict):
        # Fix if cart is not a dictionary
        session['cart'] = {}
        debug_log("Cart fixed (was not a dict)")

def get_cart_total_items():
    """Calculate total items in cart"""
    initialize_cart()
    
    try:
        if session['cart']:
            total = sum(int(qty) for qty in session['cart'].values())
            debug_log(f"Cart total items: {total}")
            return total
    except Exception as e:
        debug_log(f"Error calculating cart total: {str(e)}")
    
    return 0

def convert_usd_to_idr(usd_amount):
    """Convert USD to IDR (simulated exchange rate)"""
    try:
        amount = float(usd_amount)
        return int(amount * 15500)
    except:
        return 0

def generate_order_number():
    """Generate unique order number"""
    return f'ORD-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:8].upper()}'

@app.route('/')
def index():
    """Home page with all products"""
    try:
        debug_log("Loading index page")
        
        products = get_all_products()
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        # Log session info
        debug_log(f"Session keys: {list(session.keys())}")
        if 'cart' in session:
            debug_log(f"Cart content: {session['cart']}")
        
        # Apply search filter
        search_query = request.args.get('search', '')
        if search_query:
            products = [p for p in products if search_query.lower() in p.get('title', '').lower()]
        
        # Apply category filter
        category = request.args.get('category', '')
        if category:
            products = [p for p in products if p.get('category', '') == category]
        
        # Apply sorting
        sort_by = request.args.get('sort', '')
        if sort_by == 'price_asc':
            products.sort(key=lambda x: x.get('price', 0))
        elif sort_by == 'price_desc':
            products.sort(key=lambda x: x.get('price', 0), reverse=True)
        
        debug_log(f"Loaded {len(products)} products, cart count: {cart_count}")
        
        return render_template('index.html', 
                             products=products, 
                             categories=categories,
                             cart_count=cart_count,
                             selected_category=category)
    except Exception as e:
        debug_log(f"Error in index route: {str(e)}")
        traceback.print_exc()
        return render_template('index.html', 
                             products=[], 
                             categories=get_categories(),
                             cart_count=0,
                             selected_category='')

@app.route('/category/<name>')
def category(name):
    """Products by category"""
    try:
        debug_log(f"Loading category: {name}")
        
        response = requests.get(f'{BASE_URL}/products/category/{name}', timeout=10)
        products = response.json() if response.status_code == 200 else []
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        debug_log(f"Loaded {len(products)} products in category {name}")
        
        return render_template('index.html', 
                             products=products, 
                             categories=categories,
                             cart_count=cart_count,
                             selected_category=name)
    except Exception as e:
        debug_log(f"Error in category route: {str(e)}")
        return redirect(url_for('index'))

@app.route('/product/<int:id>')
def product_detail(id):
    """Product detail page"""
    try:
        debug_log(f"Loading product detail for ID: {id}")
        
        product = get_product_by_id(id)
        if not product:
            flash('❌ Product not found', 'error')
            debug_log(f"Product {id} not found")
            return redirect(url_for('index'))
        
        # Convert price to IDR for display
        product['price_idr'] = convert_usd_to_idr(product.get('price', 0))
        
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        debug_log(f"Product loaded: {product.get('title')}")
        
        return render_template('detail.html', 
                             product=product, 
                             categories=categories,
                             cart_count=cart_count)
    except Exception as e:
        debug_log(f"Error in product_detail: {str(e)}")
        traceback.print_exc()
        flash('❌ Error loading product details', 'error')
        return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart - FIXED VERSION"""
    try:
        debug_log(f"Adding product {product_id} to cart")
        
        # Initialize cart
        initialize_cart()
        
        # Get quantity
        quantity = int(request.form.get('quantity', 1))
        product_id_str = str(product_id)
        
        debug_log(f"Quantity: {quantity}, Product ID string: {product_id_str}")
        debug_log(f"Cart before: {session.get('cart', {})}")
        
        # Add to cart
        if product_id_str in session['cart']:
            session['cart'][product_id_str] += quantity
        else:
            session['cart'][product_id_str] = quantity
        
        # Mark session as modified
        session.modified = True
        
        debug_log(f"Cart after: {session['cart']}")
        
        flash('✅ Product added to cart successfully!', 'success')
        
        # Get referrer or default to index
        referrer = request.referrer
        if not referrer:
            referrer = url_for('index')
        
        return redirect(referrer)
        
    except Exception as e:
        debug_log(f"Error adding to cart: {str(e)}")
        traceback.print_exc()
        flash('❌ Error adding product to cart', 'error')
        return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """Cart page - FIXED VERSION"""
    try:
        debug_log("Loading cart page")
        
        # Initialize cart
        initialize_cart()
        
        cart_items = []
        total_price_usd = 0
        total_price_idr = 0
        
        debug_log(f"Cart session: {session.get('cart', {})}")
        
        if session['cart']:
            for product_id_str, quantity in session['cart'].items():
                try:
                    product_id = int(product_id_str)
                    product = get_product_by_id(product_id)
                    
                    debug_log(f"Processing product {product_id}: {product}")
                    
                    if product:
                        price = product.get('price', 0)
                        subtotal_usd = price * quantity
                        total_price_usd += subtotal_usd
                        
                        cart_items.append({
                            'id': product_id,
                            'title': product.get('title', 'Unknown Product'),
                            'price_usd': price,
                            'price_idr': convert_usd_to_idr(price),
                            'image': product.get('image', ''),
                            'quantity': quantity,
                            'subtotal_usd': round(subtotal_usd, 2),
                            'subtotal_idr': convert_usd_to_idr(subtotal_usd)
                        })
                        
                        debug_log(f"Added item: {product.get('title')} x{quantity}")
                except Exception as e:
                    debug_log(f"Error processing product {product_id_str}: {str(e)}")
                    continue
        
        total_price_idr = convert_usd_to_idr(total_price_usd)
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        debug_log(f"Cart items: {len(cart_items)}, Total: Rp {total_price_idr}")
        
        return render_template('cart.html', 
                             cart_items=cart_items, 
                             total_price_usd=round(total_price_usd, 2),
                             total_price_idr=total_price_idr,
                             categories=categories,
                             cart_count=cart_count)
    except Exception as e:
        debug_log(f"Error in cart route: {str(e)}")
        traceback.print_exc()
        return render_template('cart.html',
                             cart_items=[],
                             total_price_usd=0,
                             total_price_idr=0,
                             categories=get_categories(),
                             cart_count=0)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities - FIXED VERSION"""
    try:
        debug_log("Updating cart")
        
        # Initialize cart
        initialize_cart()
        
        debug_log(f"Form data: {dict(request.form)}")
        debug_log(f"Cart before update: {session['cart']}")
        
        # Handle remove action
        remove_id = request.form.get('remove')
        if remove_id and remove_id in session['cart']:
            del session['cart'][remove_id]
            flash('🗑️ Item removed from cart', 'info')
            debug_log(f"Removed item: {remove_id}")
        
        # Handle quantity updates
        for product_id in list(session['cart'].keys()):
            quantity_key = f'quantity_{product_id}'
            if quantity_key in request.form:
                try:
                    new_quantity = int(request.form[quantity_key])
                    if new_quantity > 0:
                        session['cart'][product_id] = new_quantity
                        debug_log(f"Updated {product_id} to {new_quantity}")
                    else:
                        del session['cart'][product_id]
                        debug_log(f"Removed {product_id} (quantity 0)")
                except ValueError as e:
                    debug_log(f"Invalid quantity for {product_id}: {str(e)}")
                    continue
        
        session.modified = True
        debug_log(f"Cart after update: {session['cart']}")
        
        flash('🔄 Cart updated successfully', 'success')
        
    except Exception as e:
        debug_log(f"Error updating cart: {str(e)}")
        traceback.print_exc()
        flash('❌ Error updating cart', 'error')
    
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    """Clear all items from cart"""
    try:
        debug_log("Clearing cart")
        
        session.pop('cart', None)
        session.modified = True
        
        debug_log("Cart cleared")
        
        flash('🗑️ Cart cleared successfully', 'info')
    except Exception as e:
        debug_log(f"Error clearing cart: {str(e)}")
        flash('❌ Error clearing cart', 'error')
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    try:
        debug_log("Loading checkout page")
        
        # Initialize cart
        initialize_cart()
        
        if not session['cart']:
            flash('🛒 Your cart is empty', 'warning')
            debug_log("Cart is empty, redirecting to cart")
            return redirect(url_for('cart'))
        
        cart_items = []
        total_price_usd = 0
        
        for product_id_str, quantity in session['cart'].items():
            try:
                product_id = int(product_id_str)
                product = get_product_by_id(product_id)
                if product:
                    price = product.get('price', 0)
                    subtotal_usd = price * quantity
                    total_price_usd += subtotal_usd
                    
                    cart_items.append({
                        'id': product_id,
                        'title': product.get('title', 'Unknown Product'),
                        'price_usd': price,
                        'price_idr': convert_usd_to_idr(price),
                        'quantity': quantity,
                        'subtotal_usd': round(subtotal_usd, 2),
                        'subtotal_idr': convert_usd_to_idr(subtotal_usd)
                    })
            except:
                continue
        
        total_price_idr = convert_usd_to_idr(total_price_usd)
        
        # Check COD maximum amount
        cod_max = PAYMENT_METHODS['cod']['max_amount']
        cod_available = total_price_idr <= cod_max
        
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        debug_log(f"Checkout: {len(cart_items)} items, Total: Rp {total_price_idr}")
        
        return render_template('checkout.html', 
                             cart_items=cart_items, 
                             total_price_usd=round(total_price_usd, 2),
                             total_price_idr=total_price_idr,
                             payment_methods=PAYMENT_METHODS,
                             categories=categories,
                             cart_count=cart_count,
                             cod_available=cod_available,
                             cod_max=cod_max)
    except Exception as e:
        debug_log(f"Error in checkout route: {str(e)}")
        traceback.print_exc()
        flash('❌ Error loading checkout page', 'error')
        return redirect(url_for('cart'))

@app.route('/checkout_details', methods=['POST'])
def checkout_details():
    """Process checkout details and redirect to payment"""
    try:
        debug_log("Processing checkout details")
        
        # Initialize cart
        initialize_cart()
        
        if not session['cart']:
            flash('🛒 Your cart is empty', 'warning')
            return redirect(url_for('cart'))
        
        # Get form data
        shipping_address = request.form.get('shipping_address', '').strip()
        customer_name = request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        payment_method = request.form.get('payment_method', '').strip()
        
        debug_log(f"Customer: {customer_name}, Payment: {payment_method}")
        
        # Validation
        if not all([shipping_address, customer_name, customer_phone, payment_method]):
            flash('❌ Please fill in all required fields', 'error')
            return redirect(url_for('checkout'))
        
        if payment_method not in PAYMENT_METHODS:
            flash('❌ Please select a valid payment method', 'error')
            return redirect(url_for('checkout'))
        
        # Calculate order total
        total_price_usd = 0
        cart_items = []
        
        for product_id_str, quantity in session['cart'].items():
            try:
                product_id = int(product_id_str)
                product = get_product_by_id(product_id)
                if product:
                    price = product.get('price', 0)
                    subtotal_usd = price * quantity
                    total_price_usd += subtotal_usd
                    
                    cart_items.append({
                        'title': product.get('title', 'Unknown Product'),
                        'quantity': quantity,
                        'price_usd': price,
                        'subtotal_usd': subtotal_usd
                    })
            except:
                continue
        
        # Add payment fee
        payment_fee_idr = PAYMENT_METHODS[payment_method]['fee']
        payment_fee_usd = payment_fee_idr / 15500
        total_with_fee_usd = total_price_usd + payment_fee_usd
        
        # Check COD limit
        total_price_idr = convert_usd_to_idr(total_with_fee_usd)
        if payment_method == 'cod' and total_price_idr > PAYMENT_METHODS['cod']['max_amount']:
            flash(f'❌ COD maximum amount is Rp {PAYMENT_METHODS["cod"]["max_amount"]:,}', 'error')
            return redirect(url_for('checkout'))
        
        # Create order
        order_id = generate_order_number()
        
        # Generate payment details based on method
        payment_details = {
            'method': payment_method,
            'order_id': order_id,
            'amount': total_price_idr,
            'expiry': datetime.now().strftime('%d %B %Y %H:%M')
        }
        
        if 'orders' not in session:
            session['orders'] = {}
        
        session['orders'][order_id] = {
            'order_id': order_id,
            'date': datetime.now().strftime('%d %B %Y %H:%M'),
            'items': cart_items,
            'customer': {
                'name': customer_name,
                'phone': customer_phone,
                'email': customer_email,
                'address': shipping_address
            },
            'total_usd': round(total_price_usd, 2),
            'total_idr': convert_usd_to_idr(total_price_usd),
            'payment_method': payment_method,
            'payment_fee_idr': payment_fee_idr,
            'total_with_fee_usd': round(total_with_fee_usd, 2),
            'total_with_fee_idr': total_price_idr,
            'payment_details': payment_details,
            'status': 'pending',
            'expiry_time': datetime.now().timestamp() + 3600
        }
        
        session.modified = True
        
        debug_log(f"Order created: {order_id}")
        
        return redirect(url_for('payment', order_id=order_id))
        
    except Exception as e:
        debug_log(f"Error in checkout_details: {str(e)}")
        traceback.print_exc()
        flash('❌ Error processing checkout', 'error')
        return redirect(url_for('checkout'))

@app.route('/payment/<order_id>')
def payment(order_id):
    """Payment page"""
    try:
        debug_log(f"Loading payment for order: {order_id}")
        
        if 'orders' not in session or order_id not in session['orders']:
            flash('❌ Order not found', 'error')
            return redirect(url_for('index'))
        
        order = session['orders'][order_id]
        
        # Check if payment expired
        if datetime.now().timestamp() > order['expiry_time']:
            flash('⏰ Payment session expired', 'error')
            return redirect(url_for('checkout'))
        
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        debug_log(f"Payment page loaded for order: {order_id}")
        
        return render_template('payment.html',
                             order=order,
                             payment_methods=PAYMENT_METHODS,
                             categories=categories,
                             cart_count=cart_count)
    except Exception as e:
        debug_log(f"Error loading payment page: {str(e)}")
        traceback.print_exc()
        flash('❌ Error loading payment page', 'error')
        return redirect(url_for('index'))

@app.route('/complete_payment/<order_id>', methods=['POST'])
def complete_payment(order_id):
    """Complete payment (simulated)"""
    try:
        debug_log(f"Completing payment for order: {order_id}")
        
        if 'orders' not in session or order_id not in session['orders']:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        order = session['orders'][order_id]
        
        # Simulate payment processing
        import time
        time.sleep(2)
        
        # Update order status
        order['status'] = 'paid'
        order['paid_at'] = datetime.now().strftime('%d %B %Y %H:%M:%S')
        order['transaction_id'] = f'TXN-{uuid.uuid4().hex[:12].upper()}'
        
        # Clear cart if payment successful
        if 'cart' in session:
            session.pop('cart', None)
        
        session.modified = True
        
        debug_log(f"Payment completed for order: {order_id}")
        
        return jsonify({
            'success': True,
            'message': 'Payment completed successfully!',
            'order_id': order_id,
            'transaction_id': order['transaction_id']
        })
        
    except Exception as e:
        debug_log(f"Error in complete_payment: {str(e)}")
        return jsonify({'success': False, 'message': 'Payment failed'})

@app.route('/order_status/<order_id>')
def order_status(order_id):
    """Order status page"""
    try:
        if 'orders' not in session or order_id not in session['orders']:
            flash('❌ Order not found', 'error')
            return redirect(url_for('index'))
        
        order = session['orders'][order_id]
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        return render_template('order_status.html',
                             order=order,
                             payment_methods=PAYMENT_METHODS,
                             categories=categories,
                             cart_count=cart_count)
    except Exception as e:
        debug_log(f"Error loading order status: {str(e)}")
        flash('❌ Error loading order status', 'error')
        return redirect(url_for('index'))

@app.route('/payment_history')
def payment_history():
    """Payment history page"""
    try:
        orders = session.get('orders', {})
        categories = get_categories()
        cart_count = get_cart_total_items()
        
        # Sort orders by date (newest first)
        sorted_orders = dict(sorted(
            orders.items(),
            key=lambda x: datetime.strptime(x[1]['date'], '%d %B %Y %H:%M'),
            reverse=True
        ))
        
        return render_template('payment_history.html',
                             orders=sorted_orders,
                             categories=categories,
                             cart_count=cart_count)
    except Exception as e:
        debug_log(f"Error in payment_history: {str(e)}")
        return render_template('payment_history.html',
                             orders={},
                             categories=get_categories(),
                             cart_count=0)

@app.route('/api/get_cart_count')
def api_get_cart_count():
    """API endpoint to get cart count"""
    try:
        cart_count = get_cart_total_items()
        return jsonify({'success': True, 'count': cart_count})
    except:
        return jsonify({'success': False, 'count': 0})

@app.route('/api/check_cod_limit')
def check_cod_limit():
    """API endpoint to check COD limit"""
    try:
        # Initialize cart
        initialize_cart()
        
        if not session['cart']:
            return jsonify({'available': False, 'message': 'Cart is empty'})
        
        total_price_usd = 0
        for product_id_str, quantity in session['cart'].items():
            try:
                product_id = int(product_id_str)
                product = get_product_by_id(product_id)
                if product:
                    total_price_usd += product.get('price', 0) * quantity
            except:
                continue
        
        total_price_idr = convert_usd_to_idr(total_price_usd)
        cod_max = PAYMENT_METHODS['cod']['max_amount']
        
        return jsonify({
            'available': total_price_idr <= cod_max,
            'total': total_price_idr,
            'limit': cod_max,
            'message': 'COD available' if total_price_idr <= cod_max else f'COD maximum is Rp {cod_max:,}'
        })
    except Exception as e:
        debug_log(f"Error checking COD limit: {str(e)}")
        return jsonify({'available': False, 'message': 'Error checking COD limit'})

@app.route('/debug_session')
def debug_session():
    """Debug session endpoint"""
    debug_info = {
        'session_keys': list(session.keys()),
        'cart': session.get('cart', {}),
        'orders': list(session.get('orders', {}).keys()) if 'orders' in session else []
    }
    return jsonify(debug_info)

@app.route('/reset_session')
def reset_session():
    """Reset session for debugging"""
    session.clear()
    session.modified = True
    return "Session cleared"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    debug_log(f"404 Error: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    debug_log(f"500 Error: {error}")
    traceback.print_exc()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')