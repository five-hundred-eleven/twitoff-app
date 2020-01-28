#!/usr/bin/env python3

import datetime
from twitoff import DB
from twitoff.models.User import User

class Tweet(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey("user.id"), nullable=False)
    text = DB.Column(DB.Unicode(280), nullable=False)
    date = DB.Column(DB.DateTime(timezone=False), default=datetime.datetime.utcnow, nullable=False)

    fk_user = DB.ForeignKeyConstraint(['user_id'], ['user.id'])

    user = DB.relationship("User", backref=DB.backref("tweets", lazy=True))
