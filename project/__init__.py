from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager








app = Flask(__name__)
app.config['SECRET_KEY'] ='8a67af50401ddca8fc961009b0c0f3f2e49bd3ef91a4b0cdb150fc83dec7469c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


# Import the routes
from project import routes