#!/usr/bin/env python3

"""
    Service for dealing with the `tweet` table in the database.
"""

import pickle

import basilica
from decouple import config
import tweepy
from sqlalchemy import func

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet
from twitoff.service import user_service

class TweetService:
    """
        Service for dealing with the `tweet` table in the database.
    """

    def getTweetsByUserId(self, user_id):
        """
            Retrieve tweets of the given user. This method deals with
            tweets stored locally and does not call the twitter API.

            @type username: int
            @rtype: List[Tweet]
        """
        print(f"Querying database for tweets from user with id {user_id}")
        res = Tweet.query.filter(Tweet.user_id == user_id).all()
        print("Success!")
        return res

    def addTweets(self, tweets):
        """
            Adds the given tweets to the database and calculates their embedding
            by using the Basilica API.

            @type tweets: List[tweepy.models.Status]
        """
        assert all(isinstance(tweet, tweepy.models.Status) for tweet in tweets)

        print("Adding tweets to database")
        print(f"First tweet: {tweets[0].full_text}")

        with basilica.Connection(config("BASILICA_KEY")) as conn:
            embeddings = list(conn.embed_sentences(
                [tweet.full_text for tweet in tweets]
            ))

        print("Successfully got basilica embeddings")

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

        print("Success!")
