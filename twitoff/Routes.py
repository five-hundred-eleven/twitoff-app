#!/usr/bin/env python3


"""
    Definition of the routes of the app.
"""


from flask import render_template

from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB
from twitoff.service import user_service, tweet_service
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet


@APP.route("/")
def indexPage():
    """
       Renders the base.html template. 
    """
    users = User.query.all()
    return render_template("base.html", users=users)


@APP.route("/user/<username>")
def userPage(username):
    """
        Renders the tweets.html template.

        @type username: str
    """

    try:
        user = user_service.getUser(username)
        tweets = tweet_service.getTweetsByUser(username)
        return render_template("tweets.html", username=user.name, tweets=tweets)

    except NoResultFound as e:
        print(e)
        return "User not found."

    except Exception as e:
        print(e)
        return "Unknown error."
