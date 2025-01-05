from flask import render_template, send_from_directory
from project import app



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