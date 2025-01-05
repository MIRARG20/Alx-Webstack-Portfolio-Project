from flask import render_template
from project import app



# Home page route.
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Home")