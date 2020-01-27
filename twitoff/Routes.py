from twitoff import APP
from flask import render_template



@APP.route("/")
def indexPage():
    return "Index page"


@APP.route("/hello")
def helloPage():
    return render_template("base.html", title="hello")


@APP.route("/user/<username>")
def userPage(username):
    return f"Hello, {username}"

