#!/usr/bin/env python3

from decouple import config
import tweepy

class TwitterService:

    def __init__(self):
        twitter_auth = tweepy.OAuthHandler(config("TWITTER_CONSUMER_API_KEY"), config("TWITTER_CONSUMER_API_SECRET"))
        twitter_auth.set_access_token(config("TWITTER_ACCESS_TOKEN"), config("TWITTER_ACCESS_TOKEN_SECRET"))
        self.__twitter = tweepy.API(twitter_auth)

    def loadUser(self, username):
        print(f"Getting twitter timeline for {username}")
        user = self.__twitter.get_user(username)
        timeline = user.timeline(count=200, exclude_replies=True, tweet_mode="extended")
        print(type(timeline), len(timeline))
        return user, timeline
