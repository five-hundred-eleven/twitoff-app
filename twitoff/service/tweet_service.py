#!/usr/bin/env python3

"""
    Service for dealing with the `tweet` table in the database.
"""

import pickle

from decouple import config
import tweepy
import basilica

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet

class TweetService:
    """
        Service for dealing with the `tweet` table in the database.
    """

    def getTweetsByUser(self, username):
        """
            Retrieve tweets of the given user. This method deals with
            tweets stored locally and does not call the twitter API.

            @type username: str
            @rtype: List[Tweet]
        """
        user = User.query.filter(User.username == username).one()
        return Tweet.query.filter(Tweet.user_id == user.id).all()

    def addTweets(self, tweets):
        """
            Adds the given tweets to the database and calculates their embedding
            by using the Basilica API.

            @type tweets: List[tweepy.models.Status]
        """
        assert all(isinstance(tweet, tweepy.models.Status) for tweet in tweets)

        with basilica.Connection(config("BASILICA_KEY")) as conn:
            embeddings = list(conn.embed_sentences(
                [tweet.full_text for tweet in tweets]
            ))

        twitoff_tweets = [
            Tweet(
                id=tweet.id,
                user_id=tweet.user.id,
                text=tweet.full_text,
                date=tweet.created_at,
                embedding=pickle.dumps(embedding),
            ) for tweet, embedding in zip(tweets, embeddings)
        ]

        DB.session.add_all(twitoff_tweets)
        DB.session.commit()
