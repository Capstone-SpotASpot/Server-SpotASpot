"""
    @file Responsible for creating the registration page for the web app
"""

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from tkinter.tix import Form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, Field
from wtforms.fields.core import SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, EqualTo, StopValidation, Optional
from wtforms import validators
from flask import flash, Flask
from typing import Optional, List, Tuple
import datetime

#--------------------------------OUR DEPENDENCIES--------------------------------#

class AddTagForm(FlaskForm):
    tag_id = StringField("Tag Id", validators=[DataRequired()])
    submit = SubmitField('Add Tag')

    def __init__(self, flaskApp: Flask,
                *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

        cls = self.__class__ # get reference to cls
