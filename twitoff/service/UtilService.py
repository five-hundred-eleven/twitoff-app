#!/usr/bin/env python3

from twitoff.service import twitter_service, user_service, tweet_service

class UtilService:

    def addUserAndTweets(self, username):

        user, tweets = twitter_service.loadUser(username)
        tweets_lst = [tweet for tweet in tweets]

        user_service.addUser(user)
        tweet_service.addTweets(tweets_lst)
