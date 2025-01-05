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