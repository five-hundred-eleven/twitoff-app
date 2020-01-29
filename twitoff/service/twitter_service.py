#!/usr/bin/env python3

"""
    Service for interfacing with the twitter API.
"""

import logging

from decouple import config
import tweepy

LOG = logging.getLogger("twitoff")

class TwitterService:
    """
        Service for interfacing with the twitter API.
    """

    def __init__(self):
        twitter_auth = tweepy.OAuthHandler(
            config("TWITTER_CONSUMER_API_KEY"),
            config("TWITTER_CONSUMER_API_SECRET"),
        )
        twitter_auth.set_access_token(
            config("TWITTER_ACCESS_TOKEN"),
            config("TWITTER_ACCESS_TOKEN_SECRET"),
        )
        self.__twitter = tweepy.API(twitter_auth)

    def loadUser(self, username):
        """
            Calls the twitter API and gets the user with the given username,
            and the user's timeline.

            @type username: str
            @rtype: tuple(tweepy.models.User, tweepy.models.ResultSet)
        """

        LOG.info(f"Getting twitter timeline for {username}")

        user = self.__twitter.get_user(username)
        timeline = user.timeline(
            count=200,
            exclude_replies=True,
            tweet_mode="extended",
        )

        LOG.info(f"{len(timeline)}")

        return user, timeline
