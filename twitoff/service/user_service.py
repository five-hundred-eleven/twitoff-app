#!/usr/bin/env python3

"""
    Service for dealing with the `user` table in the database.
"""

import tweepy
from sqlalchemy import func

from twitoff import DB
from twitoff.models.User import User

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
        print(f"Querying table for username: {username}")
        return User.query.filter(func.lower(User.username) == func.lower(username)).one()

    def getAllUsers(self):
        """
            Gets all users.

            @rtype: List[User]
        """
        print("Querying for all users")
        return User.query.all()

    def addUser(self, user):
        """
            Adds a user to the database.

            @type user: tweepy.models.User
        """
        assert isinstance(user, tweepy.models.User)
        print(f"Inserting into database: {user.name}")
        twitoff_user = User(id=user.id, name=user.name, username=user.screen_name)

        DB.session.add(twitoff_user)
        DB.session.commit()
