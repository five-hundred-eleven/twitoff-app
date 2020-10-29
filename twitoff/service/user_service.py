#!/usr/bin/env python3

"""
    Service for dealing with the `user` table in the database.
"""

import logging

import tweepy
from sqlalchemy import func

from twitoff import DB
from twitoff.models.User import User


LOG = logging.getLogger("twitoff")

class UserService:
    """
        Service for dealing with the `user` table in the database.
    """


    def getUser(self, username):
        """
            Gets the user with the given username.

            @type username: str
            @rtype: User
        """
        assert isinstance(username, str)
        LOG.info(f"Querying table for username: {username}")
        res = User.query.filter(func.lower(User.username) == func.lower(username)).one()
        LOG.info("Success!")
        return res

    def getUserById(self, user_id):
        res = User.query.filter(User.id == user_id).one()
        return res

    def getAllUsers(self):
        """
            Gets all users.

            @rtype: List[User]
        """
        LOG.info("Querying for all users")
        res = User.query.all()
        LOG.info("Success!")
        return res

    def addUser(self, user):
        """
            Adds a user to the database.

            @type user: tweepy.models.User
        """
        assert isinstance(user, tweepy.models.User)
        LOG.info(f"Inserting into database: {user.name}")
        twitoff_user = User(id=user.id, name=user.name, username=user.screen_name)

        DB.session.add(twitoff_user)
        DB.session.commit()

        LOG.info("Success!")
