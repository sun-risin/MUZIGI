from flask import Blueprint, render_template

main_blp = Blueprint("main", __name__)

@main_blp.route("/")
def home():
    return render_template("test.html")

@main_blp.route("/spoti")
def aboutSpotify():
    return render_template("test2.html")