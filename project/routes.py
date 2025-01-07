from project.models import Customer, Product, Cart, Order
from flask import render_template, url_for, flash, redirect, request, send_from_directory, abort
from project.forms import RegistrationForm, LoginForm, ShopItemsForm, CartForm
from project import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError


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



# User profile route.
@app.route("/profile")
@login_required
def profile():
    orders = Order.query.filter_by(customer_link=current_user.id).order_by(Order.id.desc()).all()
    return render_template("profile.html", title="Profile", orders=orders)



# Admin routes

# Add shop items route.
# Allows administrators to add new products to the store.
@app.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id != 1:
        abort(403)
    form = ShopItemsForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        price = form.price.data
        stock = form.stock.data
        # Check if the file is uploaded
        if not form.product_picture.data:
            flash('Please select a product picture.', 'error')
            return render_template('add-shop-items.html', form=form)
        # Get the filename
        file_name = secure_filename(form.product_picture.data.filename)
        # Set the file path
        # file_path = os.path.join(current_app.root_path, 'media', file_name)
        file_path = f'./media/{file_name}'
        try:
            # Save the file
            form.product_picture.data.save(file_path)
            new_shop_item = Product(
                    name=product_name,
                    price=price,
                    description=form.description.data,  # Add this line
                    product_picture=file_path,
                    stock=stock
                )
            db.session.add(new_shop_item)
            db.session.commit()
            flash(f'{product_name} added Successfully', 'success')
            print('Product Added')
            return render_template('add-shop-items.html', form=form)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred while adding the product: {str(e)}', 'error')
            print(f"SQLAlchemy Error: {e}")
        finally:
            db.session.close()
    return render_template('add-shop-items.html', form=form)


# Shop items route.
# Retrieves and displays products for administrators.
@app.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


# Delete item route.
# Allows administrators to delete products from the store.
@app.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')
    return render_template('404.html')


# Place order route.
@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    # Get all unpurchased items from the cart
    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
    if not cart_items:
        flash('No items in cart to purchase', 'error')
        return redirect(url_for('view_cart'))
    # Create a new order for each item in the cart
    for item in cart_items:
        new_order = Order(
            quantity=item.quantity,
            price=item.product.price,
            status="pending",
            payment_id="pending",
            customer_link=current_user.id,
            product_link=item.product.id
        )
        db.session.add(new_order)
    db.session.commit()
    flash('Order placed successfully!', 'success')
    return redirect(url_for('show_orders'))


# Show orders route.
# Displays all orders for the Admins.
@app.route('/orders')
@login_required
def show_orders():
    if current_user.id == 1:
        orders = Order.query.order_by(Order.id.desc()).all()
    else:
        orders = Order.query.filter_by(customer_link=current_user.id).order_by(Order.id.desc()).all()
    return render_template('show_orders.html', orders=orders)


@app.route('/update_order_status/<int:order_id>/<string:new_status>', methods=['POST'])
@login_required
def update_order_status(order_id, new_status):
    if current_user.id != 1:
        flash("Only administrators can update order status.", "warning")
        return redirect(url_for('show_orders'))
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    flash(f"Order #{order.id} status updated to {new_status}.", "success")
    return redirect(url_for('show_orders'))


@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    if current_user.id != 1:
        flash("Only administrators can delete orders.", "warning")
        return redirect(url_for('show_orders'))
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f"Order #{order.id} deleted successfully.", "success")
    return redirect(url_for('show_orders'))