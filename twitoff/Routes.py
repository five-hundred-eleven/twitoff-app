#!/usr/bin/env python3


"""
    Definition of the routes of the app.
"""

import logging

from flask import render_template, send_from_directory, request, redirect, flash
from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB, REDIS
from twitoff.service import user_service, tweet_service, twitter_service
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet
from twitoff.forms.AddUser import AddUser
from twitoff.forms.Twitoff import Twitoff
from twitoff.predict import do_prediction

LOG = logging.getLogger("twitoff")


@APP.route("/", methods=["GET", "POST"])
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

    if request.method == 'POST':
        LOG.info("validate")
        user1_name = request.form["user1"]
        user2_name = request.form["user2"]
        tweet = request.form["tweet"]

        user1 = user_service.getUser(user1_name)
        user2 = user_service.getUser(user2_name)

        winner, conf = do_prediction(user1, user2, tweet)
        conf *= 100

        twitoff_winner_str = f"More likely to be tweeted by {user1.name} (@{user1.username})"
        conf_str = f"Confidence: {conf:.2f}%"

    else:
        tweet = ""
        twitoff_winner_str = ""
        conf_str = ""

    cached_models = [
        key.decode("UTF-8").split("@") for key in REDIS.keys()
    ]

    return render_template(
            "index.html",
            users=users,
            form_adduser=form_adduser,
            form_twitoff=form_twitoff,
            tweet=tweet,
            twitoff_winner=twitoff_winner_str,
            conf=conf_str,
            cached_models=cached_models,
    )


@APP.route("/user/add", methods=["POST"])
def addUser():
    """
        Handles a post request to get a new user.
    """
    username = request.form["username"]
    LOG.info(f"Request to add user {username}")

    tweets = []

    try:
        user_service.getUser(username)
        LOG.info("User already exists, updating")
        _, tweets = twitter_service.loadUser(username)

    except NoResultFound:
        LOG.info("Adding user...")
        user, tweets = twitter_service.loadUser(username)
        user_service.addUser(user)

    except Exception as e:
        LOG.info(e)
        flash("Error adding user!")
        return redirect("/")

    tweets_lst = [tweet for tweet in tweets]
    tweet_service.addTweets(tweets_lst)
    return redirect(f"/user/{username}")



@APP.route("/user/<username>")
def userPage(username):
    """
        Renders the tweets.html template.

        @type username: str
    """
    try:
        user = user_service.getUser(username)
        tweets = tweet_service.getTweetsByUserId(user.id)
        return render_template("tweets.html", name=user.name, username=user.username, tweets=tweets)

    except NoResultFound as e:
        LOG.info(e)
        return "User not found."

    except Exception as e:
        LOG.info(e)
        return "Unknown error."


@APP.route("/reset", methods=["POST"])
def reset():
    """
        Resets the database.
    """
    DB.drop_all()
    DB.create_all()

    return redirect("/")


@APP.route("/js/<filename>")
def js(filename):
    LOG.info(f"serving js: {filename}")
    return send_from_directory("../static/js", filename)

@APP.route("/css/<filename>")
def css(filename):
    LOG.info(f"serving css: {filename}")
    return send_from_directory("../static/css", filename)
