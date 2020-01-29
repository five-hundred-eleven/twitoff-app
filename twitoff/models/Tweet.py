#!/usr/bin/env python3

import datetime
from twitoff import DB
from twitoff.models.User import User

class Tweet(DB.Model):
    """
        Database table for tweets.
    """
    id = DB.Column(DB.BigInteger, primary_key=True)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey("user.id"), nullable=False)
    text = DB.Column(DB.Unicode(500), nullable=False)
    date = DB.Column(DB.DateTime(timezone=False), default=datetime.datetime.utcnow, nullable=False)
    embedding = DB.Column(DB.PickleType, nullable=False)

    fk_user = DB.ForeignKeyConstraint(['user_id'], ['user.id'])

    user = DB.relationship("User", backref=DB.backref("tweets", lazy=True))
