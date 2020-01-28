#!/usr/bin/env python3

from decouple import config
import tweepy
import basilica
import pickle

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet

class TweetService:

    def getTweetsByUser(self, username):
        user = User.query.filter(User.username==username).one()
        return Tweet.query.filter(Tweet.user_id==user.id).all()

    def addTweets(self, tweets):
        assert all(isinstance(tweet, tweepy.models.Status) for tweet in tweets)

        with basilica.Connection(config("BASILICA_KEY")) as c:
            embeddings = list(c.embed_sentences(
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
