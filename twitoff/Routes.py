#!/usr/bin/env python3


"""
    Definition of the routes of the app.
"""

import logging
import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression
import basilica
from decouple import config

from flask import render_template, send_from_directory, request, redirect, flash
from sqlalchemy.orm.exc import NoResultFound

from twitoff import APP, DB
from twitoff.service import user_service, tweet_service, twitter_service
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet
from twitoff.forms.AddUser import AddUser
from twitoff.forms.Twitoff import Twitoff

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

        user1_tweets = tweet_service.getTweetsByUserId(user1.id)
        user2_tweets = tweet_service.getTweetsByUserId(user2.id)

        user1_embeddings = [
            pickle.loads(t.embedding) for t in user1_tweets
        ]
        user2_embeddings = [
            pickle.loads(t.embedding) for t in user2_tweets
        ]

        target = "target"

        user1_df = pd.DataFrame(user1_embeddings)
        user1_df[target] = [1]*len(user1_df)
        user2_df = pd.DataFrame(user2_embeddings)
        user2_df[target] = [2]*len(user2_df)

        df = pd.concat([user1_df, user2_df])
        features = df.columns.drop([target])
        X = df[features]
        y = df[target]

        model = LogisticRegression(solver="lbfgs")
        model.fit(X, y)

        with basilica.Connection(config("BASILICA_KEY")) as conn:
            emb = list(conn.embed_sentence(
                tweet,
                model="twitter",
            ))

        tweet_df = pd.DataFrame([emb])
        pred = model.predict(tweet_df)
        if pred[0] == 1:
            twitoff_winner = f"More likely to be tweeted by {user1.name} (@{user1.username})"
        elif pred[0] == 2:
            twitoff_winner = f"More likely to be tweeted by {user2.name} (@{user2.username})"
        else:
            twitoff_winner = "Unknown error"

    else:
        tweet = ""
        twitoff_winner = ""

    return render_template(
            "index.html",
            users=users,
            form_adduser=form_adduser,
            form_twitoff=form_twitoff,
            tweet=tweet,
            twitoff_winner=twitoff_winner
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
