#!/usr/bin/env python3

import tweepy

from twitoff import DB
from twitoff.models.User import User

class UserService:

    def getUser(self, username):
        return User.query.filter(User.username==username).one()

    def getAllUsers(self):
        return User.query.all()

    def addUser(self, user):
        assert isinstance(user, tweepy.models.User)

        twitoff_user = User(id=user.id, name=user.name, username=user.screen_name)

        DB.session.add(twitoff_user)
        DB.session.commit()
