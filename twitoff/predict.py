#!/usr/bin/env python3

from io import StringIO
import pickle
import logging

from decouple import config
import numpy as np
from sklearn.linear_model import LogisticRegression
import basilica

from twitoff.service import user_service, tweet_service
from twitoff.models.User import User
from twitoff import REDIS


LOG = logging.getLogger("twitoff")

def __create_model(user1, user2):
    """
        Trains a model on the two users.

        @type user1: twitoff.models.User
        @type user2: twitoff.models.User

        @rtype: LogisticRegression
    """
    LOG.info(
        f"__create_model(<User {user1.username}>,"
        f"<User {user2.username}>)"
    )
    user1_tweets = tweet_service.getTweetsByUserId(user1.id)
    user2_tweets = tweet_service.getTweetsByUserId(user2.id)

    user1_embeddings = [
        pickle.loads(t.embedding) for t in user1_tweets
    ]
    user2_embeddings = [
        pickle.loads(t.embedding) for t in user2_tweets
    ]
    X = np.vstack([user1_embeddings, user2_embeddings])
    y = np.array([1]*len(user1_embeddings) + [2]*len(user2_embeddings))

    model = LogisticRegression(solver="lbfgs")
    model.fit(X, y)

    return model


def __create_model_cached(user1, user2):
    """
        Trains a model on the two users. The user with the lower
        user id should be user1.

        @type user1: twitoff.models.User
        @type user2: twitoff.models.User

        @rtype: str
    """
    assert isinstance(user1, User)
    assert isinstance(user2, User)

    LOG.info(
        f"__create_model_cached(<User {user1.username}>,"
        f"<User {user2.username}>)"
    )

    if user1.id > user2.id:
        LOG.info("swapping users as per user id")
        user1, user2 = user2, user1
    
    key = user1.username + user2.username
    model = REDIS.get(key)

    if not model:
        model = __create_model(user1, user2)
        val = pickle.dumps(model)
        REDIS.set(key, val)
    else:
        model = pickle.loads(model)
        LOG.info("Cached model found!")

    return model


def do_prediction(user1, user2, tweet):
    """
        Trains a LogisticRegression on the tweets of the
        two users and then predicts which user is more
        likely to tweet the given tweet.

        Returns a tuple of the User who is the winner,
        and the confidence as a percentage.

        @type user1_name: twitoff.models.User
        @type user2_name: twitoff.models.User
        @type tweet: str

        @rtype: Tuple(twitoff.models.User, float)
    """
    LOG.info(
        f"do_prediction(<User {user1.username}>,"
        f"<User {user2.username}>,"
        f"{tweet})"
    )

    model = __create_model_cached(user1, user2)
    with basilica.Connection(config("BASILICA_KEY")) as conn:
        emb = list(conn.embed_sentence(
            tweet,
            model="twitter",
        ))
    emb_arr = np.array([emb])

    # assert shape is (1,)
    pred, = model.predict_proba(emb_arr)

    u1_ix, = np.where(model.classes_ == 1)
    u2_ix, = np.where(model.classes_ == 2)
    if pred[u1_ix] > pred[u2_ix]:
        return user1, pred[u1_ix][0]

    return user2, pred[u2_ix][0]
