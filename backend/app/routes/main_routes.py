from flask import Blueprint, render_template

main_blp = Blueprint("main", __name__)

@main_blp.route("/")
def home():
    return render_template("test.html")