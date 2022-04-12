#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------STANDARD DEPENDENCIES-----------------------------#


#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user, login_required
from userManager import UserManager

#--------------------------------Project Includes--------------------------------#
from flask_helpers import flash_print, is_form, clear_flashes
from addCarForm import AddCarForm
from addTagForm import AddTagForm


class CarRoutes():
    """An object responsible for all the flask/website interactions involving car features"""
    def __init__(self, app: Flask, user_manager: UserManager):
        """Initialize the CarRoutes class that works with the flask app

        Args:
            app (Flask): An existing flask app to extend
            user_manager (UserManager): The user manager class containing references to the db
        """
        self.app = app
        self.user_manager = user_manager
        self.createCarRoutes()

    def createCarRoutes(self):
        @self.app.route("/cars/add_tag", methods=["POST", "GET"], defaults={"tag_id": None})
        @self.app.route("/cars/add_tag?tag_id=<tag_id>", methods=["POST", "GET"])
        def add_tag(tag_id: int):
            """Returns the newly created tag's id"""
            if request.method == "POST":
                args = None
                tag_id = None

                is_form = len(request.form) > 0

                if is_form:
                    add_tag_form = AddTagForm(self.app, request.form)

                if is_form and add_tag_form.validate_on_submit():
                    tag_id = add_tag_form.tag_id.data
                elif is_form:
                    # flash_print(f"Add Tag Fail! Bad form", "is-warning")
                    tag_id = None
                else:
                    # make sure posting with normal method (not via form) still works
                    args = request.args
                    tag_id = args.get("tag_id")

                # dont add the tag if the data is bad
                created_tag_id = None
                print(f"Adding New Tag with real id : {tag_id}")

                if tag_id is not None:
                    created_tag_id = self.user_manager.add_tag(tag_id)

                # how the return gets handled depends if a form or curl was used
                if not is_form:
                    return {"new_tag_id": created_tag_id}
                else:
                    # make a fresh form to use for the page
                    fresh_form=AddTagForm(self.app)
                    fresh_form.tag_id.data = ""
                    return render_template("add_tag.html", title="Add Car", form=fresh_form, tag_add_success=True)

            elif request.method == "GET":
                clear_flashes(session)
                add_tag_form = AddTagForm(self.app)
                return render_template("add_tag.html", title="Add New Tag", form=add_tag_form, tag_add_success=False)

        @self.app.route("/cars/add_car", methods=["POST", "GET"], defaults={'front_tag': None, 'middle_tag': None, 'rear_tag': None})
        @self.app.route("/cars/add_car?front_tag=<front_tag>&middle_tag=<middle_tag>&rear_tag=<rear_tag>", methods=["POST", "GET"])
        @login_required
        def add_car(front_tag: int, middle_tag: int, rear_tag: int):
            args = request.args
            user_id = current_user.id
            front_tag = args.get("front_tag")
            middle_tag = args.get("middle_tag")
            rear_tag = args.get("rear_tag")

            is_form = len(request.form) > 0

            if is_form:
                add_car_form = AddCarForm(self.app, self.user_manager, request.form)

            if request.method == "POST":
                if is_form and add_car_form.validate_on_submit():
                    front_tag = add_car_form.front_tag.data
                    middle_tag = add_car_form.middle_tag.data
                    rear_tag = add_car_form.rear_tag.data
                elif is_form:
                    # flash_print(f"Add Car Fail! Bad form", "is-warning")
                    front_tag = middle_tag = rear_tag = None
                else:
                    # make sure posting with normal method (not via form) still works
                    args = request.args
                    front_tag = args.get("front_tag")
                    middle_tag = args.get("middle_tag")
                    rear_tag = args.get("rear_tag")

                # dont add tag if bad data
                print("Adding car with tags ({}, {}, {})".format(
                    front_tag, middle_tag, rear_tag))
                if user_id == None or front_tag == None or middle_tag == None or rear_tag == None:
                    new_car_id = -1
                else:
                    new_car_id = self.user_manager.add_car(user_id, front_tag, middle_tag, rear_tag)

                # if done through the webpage, redirect to a webpage with flash.
                # Otherwise just return the car id
                if not is_form:
                    return {"new_car_id": new_car_id}
                else:
                    car_add_success = new_car_id > -1
                    # Use a fresh form on success, the previous one otherwise
                    if car_add_success is True:
                        form=AddCarForm(self.app, self.user_manager)
                        form.front_tag.data = ""
                        form.middle_tag.data = ""
                        form.rear_tag.data = ""
                        return render_template("add_car.html", title="Add Car", form=form, car_add_success=True)
                    else:
                        return render_template("add_car.html", title="Add Car", form=add_car_form, car_add_success=False)

            elif request.method == "GET":
                clear_flashes(session)
                add_car_form = AddCarForm(self.app, self.user_manager)
                return render_template("add_car.html", title="Add Car", form=add_car_form, car_add_success=False)
