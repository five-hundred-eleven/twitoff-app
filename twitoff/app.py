#!/usr/bin/env python3

from decouple import config
from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

def make_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config("DATABASE_URL")
    app.config['SECRET_KEY'] = config("SECRET_KEY")
    db = SQLAlchemy(app)
    return app, db
