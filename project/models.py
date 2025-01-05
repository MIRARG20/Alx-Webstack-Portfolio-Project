from project import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader function.
    Loads a user object based on the user_id.
    :param user_id: Integer ID of the user
    :return: User object or None if not found
    """
    return Customer.query.get(int(user_id))


class Customer(db.Model, UserMixin):
    # Represents a registered user in the system.
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password = db.Column(db.String(length=70), nullable=False, unique=True)
    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))
    
    def __repr__(self):
        return f"Customer('{self.username}', '{self.email}')"
    

class Product(db.Model):
    # Represents a product available in the store.
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    stock = db.Column(db.Integer(), nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.now())
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return f"<Product(name='{self.name}', price={self.price}, stock={self.stock}, added_on={self.date_added.strftime('%Y-%m-%d')})>"




class Cart(db.Model):
    # Represents a shopping cart for customers.
    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), nullable=False)
    customer_link = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return f"<Cart(id={self.id}, product_id={self.product_link}, quantity={self.quantity}, customer_id={self.customer_link})>"
    



class Order(db.Model):
    # Represents an order placed by a customer.
    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


    def __str__(self):
        return f"<Order(id={self.id}, status='{self.status}', price={self.price})>"
