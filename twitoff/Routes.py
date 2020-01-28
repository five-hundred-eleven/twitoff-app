from flask import render_template

from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet


@APP.route("/")
def helloPage():
    users = User.query.all()
    return render_template("base.html", users=users)


@APP.route("/user/<username>")
def userPage(username):

    try:
        user = User.query.filter(User.name==username).one()
        return render_template("tweets.html", user=user)


    except NoResultFound:
        return "User not found."

