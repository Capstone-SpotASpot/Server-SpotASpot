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
from userManager import UserManager

class AddCarForm(FlaskForm):
    front_tag = StringField("Front Tag", validators=[DataRequired()])
    middle_tag = StringField("Middle Tag", validators=[DataRequired()])
    rear_tag = StringField("Rear Tag",  validators=[DataRequired()])
    submit = SubmitField('Add Car')

    def __init__(self, flaskApp: Flask,
                 user_manager : UserManager,
                *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

        cls = self.__class__ # get reference to cls
        AddCarForm._user_manager : UserManager = user_manager

        cls.front_tag = StringField('Front Tag', validators=[DataRequired(), self.validateTagExists])
        cls.middle_tag = StringField('Middle Tag', validators=[DataRequired(), self.validateTagExists])
        cls.rear_tag = StringField('Rear Tag', validators=[DataRequired(), self.validateTagExists])

    def validateTagExists(self, form : Form, field : Field) -> bool:
        """
            \n@Returns True = tag exist
        """
        # check that username is not already taken
        if not self._user_manager.does_real_tag_id_exist(field.data):
            readable_field_name = str(field.name).replace("_", " ")
            errMsg = f"Invalid Tag for {readable_field_name} position"
            # flash(errMsg, "is-danger")
            raise StopValidation(message=errMsg) # prints under box
        else:
            return True
