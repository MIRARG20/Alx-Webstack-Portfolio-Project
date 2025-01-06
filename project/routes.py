from project.models import Customer
from flask import render_template, url_for, flash, redirect, send_from_directory
from project.forms import RegistrationForm, LoginForm, ShopItemsForm, CartForm
from project import app, bcrypt, db
from flask_login import login_user, current_user, logout_user







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