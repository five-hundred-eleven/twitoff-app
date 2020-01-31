#!/usr/bin/env python3

"""
    Service for dealing with the `tweet` table in the database.
"""

import pickle
import logging

import basilica
from decouple import config
import tweepy
from sqlalchemy import func

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet
from twitoff import REDIS


LOG = logging.getLogger("twitoff")

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
        LOG.info(f"Querying database for tweets from user with id {user_id}")
        res = Tweet.query.filter(Tweet.user_id == user_id).all()
        LOG.info("Success!")
        return res

    def addTweets(self, tweets):
        """
            Adds the given tweets to the database and calculates their embedding
            by using the Basilica API.

            @type tweets: List[tweepy.models.Status]
        """
        assert all(isinstance(tweet, tweepy.models.Status) for tweet in tweets)
        
        LOG.info("Adding tweets to database")

        if len(tweets) == 0:
            LOG.info("No tweets found!")
            return

        first_tweet = tweets[0]
        user = User.query.get(first_tweet.user.id)
        LOG.info(f"First tweet: {first_tweet.full_text}")

        # invalidate redis cache for the user
        keys = [
            key for key in REDIS.keys()
            if str(key).startswith(user.username) or str(key).endswith(user.username)
        ]
        LOG.info(f"Found {len(keys)} cached models for the user, invalidating them")
        for key in keys:
            REDIS.delete(key)

        # get basilica embeddings
        with basilica.Connection(config("BASILICA_KEY")) as conn:
            embeddings = list(conn.embed_sentences(
                [tweet.full_text for tweet in tweets],
                model="twitter",
            ))

        LOG.info("Successfully got basilica embeddings")

        twitoff_tweets = [
            Tweet(
                id=tweet.id,
                user_id=tweet.user.id,
                text=tweet.full_text[:500],
                date=tweet.created_at,
                embedding=pickle.dumps(embedding),
            ) for tweet, embedding in zip(tweets, embeddings)
            if not Tweet.query.get(tweet.id)
        ]

        DB.session.add_all(twitoff_tweets)
        DB.session.commit()

        LOG.info("Success!")
