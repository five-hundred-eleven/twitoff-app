#!/usr/bin/env python3

from twitoff import DB

class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(50), nullable=False)
    username = DB.Column(DB.String(50), nullable=False)
