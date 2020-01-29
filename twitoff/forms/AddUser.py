#!/usr/bin/env python3

"""
    Contains the form for adding a twitter user.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AddUser(FlaskForm):
    """
        Contains the form for adding a twitter user.
    """
    username = StringField("Twitter Username", validators=[DataRequired()])
    submit = SubmitField("Add User", id="submitadduser")
