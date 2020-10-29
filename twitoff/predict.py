#!/usr/bin/env python3

from io import StringIO
import pickle
import joblib
import logging

from decouple import config
import numpy as np
from sklearn.linear_model import LogisticRegression
from simpletransformers.classification import ClassificationModel


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
    
    key = user1.username + "@" + user2.username
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

    if user1.id > user2.id:
        LOG.info("swapping users as per user id")
        user1, user2 = user2, user1

    #model = __create_model_cached(user1, user2)
    """
    with basilica.Connection(config("BASILICA_KEY")) as conn:
        emb = list(conn.embed_sentence(
            tweet,
            model="twitter",
        ))
    """
    tweets_df = tweet_service.getAllTweetsAsDF()
    cls = ClassificationModel("roberta", "roberta-base", use_cuda=False)
    cls.train_model(tweets_df)

    # assert shape is (1,)
    pred, raw = cls.predict([tweet])

    user = user_service.getUserById(pred[0])
    return user, 1.
