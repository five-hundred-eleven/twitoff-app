#!/usr/bin/env python3

"""
    App base.
        - APP: flask app object
        - DB: sqlalchemy database
        - UTIL: utility methods
"""

import logging

from twitoff.app import make_app

APP, DB = make_app()

from twitoff import Routes
from twitoff.service.util_service import UtilService

UTIL = UtilService()

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("twitoff")
