#!/usr/bin/env python3

from twitoff import DB
from twitoff.models.User import User
from twitoff.models.Tweet import Tweet


users = User.query.all()
for user in users:
    print("User:", user.name)
    print("\tTweets:")

    for t in user.tweets:
        print("\t\t", t.text)

    print()
