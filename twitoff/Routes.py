from flask import render_template

from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet



@APP.route("/")
def indexPage():
    return "Index page"


@APP.route("/hello")
def helloPage():
    return render_template("base.html", title="hello")


@APP.route("/user/<username>")
def userPage(username):

    try:
        user = User.query.filter(User.name==username).one()
        return render_template("tweets.html", user=user)


    except NoResultFound:
        return "User not found."

