#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from userManager import UserManager

#--------------------------------Project Includes--------------------------------#


class MobileRoutes():
    """An object responsible for all the flask/website interactions involving mobile features"""
    def __init__(self, app: Flask, user_manager: UserManager):
        """Initialize the MobileRoutes class that works with the flask app

        Args:
            app (Flask): An existing flask app to extend
            user_manager (UserManager): The user manager class containing references to the db
        """
        self.app = app
        self.user_manager = user_manager
        self.createMobileRoutes()

    def createMobileRoutes(self):
        """All routes requests from the Mobile App"""

        @self.app.route("/mobile/get_spot_coord/<int:spot_id>", methods=["GET"])
        def get_coord_from_spot_id(spot_id: int):
            """:returns {latitude: float, longitude: float}"""
            return self.self.user_manager.get_coord_from_spot_id(spot_id)

        @self.app.route("/mobile/get_is_spot_taken/<int:reader_id>")
        def get_is_spot_taken(reader_id: int) -> bool:
            """Given a reader_id, returns the status of the spots it can reach.
            :return {<spot_id>: <status>, <spot_id>: <status>}"""
            return flask.jsonify(self.self.user_manager.is_spot_taken(reader_id))

        @self.app.route("/mobile/get_local_readers", methods=["GET"], defaults={'radius': None, 'latitude': None, 'longitude': None})
        @self.app.route("/mobile/get_local_readers?radius=<radius>&latitude=<latitude>&longitude=<longitude>", methods=["GET"])
        def get_local_readers(radius: float, latitude: float, longitude: float):
            args = request.args
            try:
                radius = float(args.get('radius')) if args.get('radius') is not None else None
                center_latitude = float(args.get('latitude')) if args.get('latitude') is not None else None
                center_longitude  = float(args.get('longitude')) if args.get('longitude') is not None else None
            except Exception as err:
                print(f"Error parsing inputs to /mobile/get_local_readers. Error = {err}")
                radius = None
                center_latitude = None
                center_longitude = None

            """Given GPS coordiantes and a radius,
            returns a list of dictionaries containing all readers in that radius"""
            # if the request is not fully formed, do not accept it
            if radius is not None and center_latitude is not None and center_longitude is not None:
                # only return the reader's id and their gps coords that match
                return flask.jsonify(
                    self.self.user_manager.get_readers_in_radius(
                        center_latitude,
                        center_longitude,
                        radius
                    )
                )
            else:
                return "Parameters are missing\n"
