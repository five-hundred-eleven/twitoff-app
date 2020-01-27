#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def make_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_db.sqlite'
    db = SQLAlchemy(app)
    return app, db
