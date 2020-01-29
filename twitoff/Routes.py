#!/usr/bin/env python3


"""
    Definition of the routes of the app.
"""


from flask import render_template, send_from_directory, request, redirect, flash

from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB
from twitoff.service import user_service, tweet_service, twitter_service
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet
from twitoff.forms.AddUser import AddUser
from twitoff.forms.Twitoff import Twitoff


@APP.route("/")
def indexPage():
    """
       Renders the base.html template. 
    """
    users = User.query.all()
    form_adduser = AddUser()

    form_twitoff = Twitoff()
    user_select = [
        (user.username, f"{user.name} (@{user.username})")
        for user in users
    ]
    form_twitoff.user1.choices = user_select
    form_twitoff.user2.choices = user_select

    return render_template("index.html", users=users, form_adduser=form_adduser, form_twitoff=form_twitoff)


@APP.route("/user/add", methods=["POST"])
def addUser():
    """
        Handles a post request to get a new user.
    """
    username = request.form["username"]
    print(f"Request to add user {username}")

    try:
        user = user_service.getUser(username)
        flash("User already loaded!")
        return redirect(f"/user/{username}")

    except NoResultFound:
        pass

    try:

        user, tweets = twitter_service.loadUser(username)
        tweets_lst = [tweet for tweet in tweets]

        user_service.addUser(user)
        tweet_service.addTweets(tweets_lst)

        return redirect(f"/user/{username}")

    except:
        flash("Error adding user!")
        return redirect("/")

@APP.route("/user/<username>")
def userPage(username):
    """
        Renders the tweets.html template.

        @type username: str
    """

    try:
        user = user_service.getUser(username)
        tweets = tweet_service.getTweetsByUserId(user.id)
        return render_template("tweets.html", username=user.name, tweets=tweets)

    except NoResultFound as e:
        LOG.info(e)
        return "User not found."

    except Exception as e:
        LOG.info(e)
        return "Unknown error."


@APP.route("/js/<filename>")
def js(filename):
    print(f"serving js: {filename}")
    return send_from_directory("../static/js", filename)

@APP.route("/css/<filename>")
def css(filename):
    print(f"serving css: {filename}")
    return send_from_directory("../static/css", filename)
