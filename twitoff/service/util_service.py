#!/usr/bin/env python3

"""
    Utility for retrieving a user from twitter and adding the info to the
    local database.
"""

from twitoff.service import twitter_service, user_service, tweet_service

class UtilService:
    """
        Utility for retrieving a user from twitter and adding the info to the
        local database.
    """

    def addUserAndTweets(self, username):
        """
            Retrieves data on the user's profile and recent tweets
            and stores it in the local database.
        """

        user, tweets = twitter_service.loadUser(username)
        tweets_lst = [tweet for tweet in tweets]

        user_service.addUser(user)
        tweet_service.addTweets(tweets_lst)
