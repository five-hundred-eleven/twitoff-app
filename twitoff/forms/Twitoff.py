#!/usr/bin/env python3

"""
    Contains the form for adding a twitter user.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class Twitoff(FlaskForm):
    """
        Contains the form for adding a twitter user.
    """
    user1 = SelectField("Select a twitter user", id="first-user-input", validators=[DataRequired()])
    user2 = SelectField("Select a second twitter user", id="second-user-input", validators=[DataRequired()])
    tweet = StringField(id="tweet-input", widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(id="twitoff-submit")
