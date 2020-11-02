#!/usr/bin/env python3

from io import StringIO
import pickle
import joblib
import logging

from decouple import config
import numpy as np
import pandas as pd
from scipy.stats import mode
from sklearn.linear_model import LogisticRegression
#from simpletransformers.classification import ClassificationModel
import re
import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from twitoff.service import user_service, tweet_service
from twitoff.models.User import User
from twitoff import REDIS


LOG = logging.getLogger("twitoff")

__nlp = English()
__tokenizer = Tokenizer(__nlp.vocab)

def simple_tokenize(doc):
    """
        Takes a document and returns a list of tokens (simplified lowercase words).
        This version of the method assumes the doc is already relatively clean
        and will not handle html tags or extraneous characters.
        @type doc: str
        @rtype: List[str]
    """
    return " ".join([
        re.sub(r"[^a-z0-9]", "", t.lemma_.lower()).strip() for t in __tokenizer(doc)
        if not t.is_stop and not t.is_punct and t.text.strip()
    ])

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

    user1_text = [
        [t.text, 0] for t in user1_tweets
    ]
    user2_text = [
        [t.text, 1] for t in user2_tweets
    ]

    user1_text, user1_y = zip(*user1_text)
    user2_text, user2_y = zip(*user2_text)

    df = pd.DataFrame({"tokens": user1_text + user2_text})
    df["tokens"] = df["tokens"].apply(simple_tokenize)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["tokens"])

    nn = NearestNeighbors(n_neighbors=5)
    nn.fit(X)

    y = user1_y + user2_y

    return (vectorizer, nn, y)


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
    
    key = "@" + user1.username + "@" + user2.username
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

    vectorizer, nn, y = __create_model_cached(user1, user2)

    tokens = simple_tokenize(tweet)
    vectors = vectorizer.transform([tokens])
    _, indices = nn.kneighbors(vectors)
    pred = mode([y[ix] for ix in indices[0]])[0]

    print(pred)

    if pred[0] == 0:
        return user1, 1.

    return user2, 1.
