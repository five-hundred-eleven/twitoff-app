#!/usr/bin/env python3

"""
    This directory contains app services for interfacing with
    the databases and external APIs.

    These objects should be treated as singletons; import
    the objects initialized in this directory rather than
    re-initializing them.
"""


from twitoff.service.twitter_service import TwitterService
from twitoff.service.user_service import UserService
from twitoff.service.tweet_service import TweetService

twitter_service = TwitterService()
user_service = UserService()
tweet_service = TweetService()
