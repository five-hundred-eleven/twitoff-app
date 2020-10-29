#!/usr/bin/env python3

"""
    App base.
        - APP: flask app object
        - DB: sqlalchemy database
        - UTIL: utility methods
"""

import logging

from twitoff.app import make_app

APP, DB, REDIS = make_app()
application = APP
LOG = logging.getLogger("twitoff")

from twitoff import Routes
from twitoff.service.util_service import UtilService

UTIL = UtilService()

logging.basicConfig(level=logging.DEBUG)

