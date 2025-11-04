from flask import Blueprint, render_template

main_blp = Blueprint("main", __name__)

@main_blp.route("/")
def home():
    return render_template("test.html")
    # return render_template("test2.html") # spotify 액세스토큰 테스트페이지