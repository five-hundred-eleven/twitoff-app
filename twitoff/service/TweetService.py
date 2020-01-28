#!/usr/bin/env python3

import tweepy

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet

class TweetService:

    def getTweetsByUser(self, username):
        user = User.query.filter(User.username==username).one()
        return Tweet.query.filter(Tweet.user_id==user.id).all()

    def addTweets(self, tweets):
        assert all(isinstance(tweet, tweepy.models.Status) for tweet in tweets)

        twitoff_tweets = [
            Tweet(
                id=tweet.id,
                user_id=tweet.user.id,
                text=tweet.full_text,
                date=tweet.created_at,
            ) for tweet in tweets
        ]

        DB.session.add_all(twitoff_tweets)
        DB.session.commit()
