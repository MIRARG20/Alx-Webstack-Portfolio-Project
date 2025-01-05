from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



# Create the main application instance
app = Flask(__name__)

# Configure the application secret key
app.config['SECRET_KEY'] ='8a67af50401ddca8fc961009b0c0f3f2e49bd3ef91a4b0cdb150fc83dec7469c'

# Configure the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# Enable SQLALCHEMY_TRACK_MODIFICATIONS for better performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



# Define a custom error handler for 404 Not Found errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Initialize SQLAlchemy with the Flask application
db = SQLAlchemy(app)

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize LoginManager for user authentication
login_manager = LoginManager(app)


# Import the routes
from project import routes