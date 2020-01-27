#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def make_app():
    app = Flask(__name__)
    db = SQLAlchemy(app)
    return app, db
