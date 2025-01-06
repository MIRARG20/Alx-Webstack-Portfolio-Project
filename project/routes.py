from project.models import Customer, Product, Cart
from flask import render_template, url_for, flash, redirect, request, send_from_directory
from project.forms import RegistrationForm, LoginForm, CartForm
from project import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required




# Home page route.
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Home")


# About page route.
@app.route("/about")
def about():
    return render_template('about.html', title="About")


# Serve images from the media folder.
@app.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)



# User registration route.
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # validation on submit method
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        customer = Customer(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(customer)
        db.session.commit()
        flash(f'Account created successfully for {form.username.data}', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


# User login route.
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form = LoginForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer and bcrypt.check_password_hash(customer.password, form.password.data):
            login_user(customer, remember=form.remember.data)
            flash('You have been loged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, please check your username and password', 'error')
    return render_template('login.html', title="Login", form=form)


# Logout user route.
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


#Products page route.
@app.route("/products")
def products():
    items = Product.query.all()
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(customer_link=current_user.id).all()
    else:
        cart = []
    return render_template('products.html', title="Products", items=items, cart=cart)


# Add to cart route.
@app.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    if item_to_add and item_to_add.stock > 0:
        item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
        if item_exists:
            try:
                item_exists.quantity += 1
                item_to_add.stock -= 1
                db.session.commit()
                flash(f'Quantity of {item_exists.product.name} has been updated', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Quantity of {item_exists.product.name} not updated', 'error')
        else:
            new_cart_item = Cart(
                product_link=item_id,
                customer_link=current_user.id,
                quantity=1
            )
            item_to_add.stock -= 1
            try:
                db.session.add(new_cart_item)
                db.session.commit()
                
                flash(f'{new_cart_item.product.name} added to cart', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'{new_cart_item.product.name} has not been added to cart', 'error')
        return redirect(request.referrer)
    flash('Item out of stock or does not exist', 'error')
    return redirect(url_for('products'))



# View cart route.
# Displays the user's shopping cart and allows them to place an order
@app.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    final_cost = sum(item.product.price * item.quantity for item in cart)
    cart_form = CartForm()
    if cart_form.validate_on_submit():
        return redirect(url_for('place_order'))
    return render_template('cart.html', cart=cart, final_cost=final_cost, form=cart_form)


# Update cart quantity route.
# Allows users to change the quantity of items in their cart.
@app.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    if current_user.is_authenticated:
        cart_item = Cart.query.filter_by(customer_link=current_user.id, product_link=product_id).first()
        if cart_item:
            cart_item.quantity = request.form['quantity']
            db.session.commit()
    return redirect(url_for('view_cart'))


# Remove from cart route.
# Removes an item from the user's shopping cart.
@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    if current_user.is_authenticated:
        cart_item = Cart.query.filter_by(customer_link=current_user.id, product_link=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    return redirect(url_for('view_cart'))
