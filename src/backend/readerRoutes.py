#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from typing import TypedDict


#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from userManager import UserManager

#--------------------------------Project Includes--------------------------------#


class SendEventDataRes(TypedDict):
    is_car_parked: bool
    car_detected: int
    detection_id: int
    parked_spot_id: int

class ReaderRoutes():
    """An object responsible for all the flask/website interactions involving reader features"""
    def __init__(self, app: Flask, user_manager: UserManager):
        """Initialize the ReaderRoutes class that works with the flask app

        Args:
            app (Flask): An existing flask app to extend
            user_manager (UserManager): The user manager class containing references to the db
        """
        self.app = app
        self.user_manager = user_manager
        self.createReaderPostRoutes()

    def createReaderPostRoutes(self):
        """All routes for receiving information from the reader's"""
        @self.app.route("/reader/add_reader", methods=["POST"], defaults={'lat': None, 'long':None, 'range':None, 'bearing': None})
        @self.app.route("/reader/add_reader?lat=<lat>&long=<long>&range=<range>&bearing=<bearing>", methods=["POST"])
        def add_new_reader(lat: float, long: float, range: float, bearing: float):
            """Add a new reader given latitude, longitude, reader_range, reader_front_bearing"""
            args = request.args

            lat = args.get("lat")
            long = args.get("long")
            range = args.get("range")
            reader_front_bearing = args.get("bearing")

            # dont add reader if bad data
            if lat == None or long == None or range == None or reader_front_bearing == None:
                new_reader_id = -1
            else:
                new_reader_id = self.user_manager.add_reader(lat, long, range, reader_front_bearing)

            return {
                "new_reader_added": new_reader_id
            }

        @self.app.route("/reader/send_event_data", defaults={'reader_id': None, 'tag_id': None, 'signal_strength': None}, methods=["POST"])
        @self.app.route("/reader/send_event_data?reader_id=<reader_id>&tag_id=<tag_id>&signal_strength=<signal_strength>", methods=["POST"])
        def reader_send_event_data(reader_id, tag_id, signal_strength) -> SendEventDataRes:
            """
            \n:brief Stores the event in the correct database table and ensures the data is processed
            \nParams: reader_id, tag_id, and signal_stregth
            \nTest: curl -X POST "http://localhost:31025/reader/send_event_data?reader_id=2&tag_id=4"
            """
            # Receive + Store data from reader
            args = request.args
            is_valid_arg    = lambda x: x != None # and (x != -1 and x != -1.0)
            sanitize_choice = lambda x, y: x if is_valid_arg(x) else (y if is_valid_arg(y) else -1)
            reader_id       = int(sanitize_choice(reader_id, args.get('reader_id')))
            tag_id          = int(sanitize_choice(tag_id, args.get('tag_id')))
            signal_strength = float(sanitize_choice(args.get('signal_strength'), -1.0))

            # if any param is -1, dont run bc will error
            invalid_ret = {
                "is_car_parked": False,
                "car_detected": None,
                "detection_id": None,
                "parked_spot_id": None
            }
            if not is_valid_arg(reader_id):
                print(f"Invalid reader_send_event_data() reader_id={reader_id}")
                return invalid_ret
            elif not is_valid_arg(tag_id):
                print(f"Invalid reader_send_event_data() tag_id={tag_id}")
                return invalid_ret

            timestamp = datetime.now()
            readeable_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # try to add observation event to the db
            observation_id = self.user_manager.add_observation_event(
                readeable_timestamp,
                signal_strength,
                reader_id,
                tag_id
            )
            if (observation_id == -1):
                # skip detection if there was an error observing
                print(f"Failed: add_observation_event({(readeable_timestamp, signal_strength, reader_id, tag_id)})")
                return invalid_ret

            # run algorithm to see if a detection was made
            detect_res = self.user_manager.run_detect_algo(observation_id)
            # provide scope for vars and default to already known values
            car_id = detect_res['car_id'] if detect_res else -1
            detect_id = -1
            spot_id = -1

            # fill in rest of return json if car completely detected and have all the info
            if(detect_res != None and detect_res['is_car_parked'] is True):
                # car is detected as parked so mark in db
                print("Calling add_detection_and_park_car({0}, {1}, {2}, {3})".format(
                    detect_res['reader_id'],
                    detect_res['observation1_id'],
                    detect_res['observation2_id'],
                    detect_res['observation3_id']
                ))
                detect_car_spot_dict = self.user_manager.add_detection_and_park_car(
                    detect_res['reader_id'], detect_res['observation1_id'],
                    detect_res['observation2_id'], detect_res['observation3_id']
                )

                if (detect_car_spot_dict != None):
                    car_id = detect_car_spot_dict['parked_car_id']
                    detect_id = detect_car_spot_dict['created_detect_id']
                    spot_id = detect_car_spot_dict['parked_spot_id']

            return {
                "is_car_parked": bool(detect_res['is_car_parked']) if detect_res else False,
                "car_id": car_id,
                "detection_id": detect_id,
                "parked_spot_id": spot_id
            }
