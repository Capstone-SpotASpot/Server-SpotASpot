#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os, sys
import webbrowser # allows opening of new tab on start
import argparse # cli paths
import logging # used to disable printing of each POST/GET request
import pathlib
from pathlib import Path
import secrets
import getpass
from datetime import  datetime
from typing import TypedDict, List, Tuple

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import werkzeug.serving # needed to make production worthy app that's secure

# decorate app.route with "@login_required" to make sure user is logged in before doing anything
# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader -- "flask_login.login_required"
from flask_login import login_user, current_user, login_required, logout_user


#--------------------------------Project Includes--------------------------------#
from user import User
from userManager import UserManager
from db_manager import DB_Manager
from flask_helpers import FlaskHelper

class SendEventDataRes(TypedDict):
    is_car_parked: bool
    car_detected: int
    detection_id: int
    parked_spot_id: int

class WebApp(UserManager):
    def __init__(self, port: int, is_debug: bool, user: str, pwd: str, db: str, db_host: str):
        self._app = Flask("SpotASpot_ServerApp")
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True # refreshes flask if html files change
        self._app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

        # Inheret all functions and 'self' variables (UserManager)
        UserManager.__init__(self, self._app, user, pwd, db, db_host)
        self.flask_helper = FlaskHelper(self._app, port)

        # flask dir paths
        backend_dir = Path(__file__).parent.resolve()
        src_dir = backend_dir.parent
        frontend_dir = src_dir / 'frontend'
        template_dir = frontend_dir / 'templates'
        static_dir = frontend_dir / "static"
        self._app.static_folder = str(static_dir)
        self._app.template_folder = str(template_dir)

        # logging
        self._logger = logging.getLogger("werkzeug")

        self._is_debug = is_debug
        self._host = '0.0.0.0'
        self._port = port
        logLevel = logging.INFO if self._is_debug == True else logging.ERROR
        self._logger.setLevel(logLevel)

        # create routes (and print routes)
        self.generateRoutes()
        self.flask_helper.print_routes()

        # dont thread so requests dont happen concurrently
        is_threaded = True

        # start blocking main web server loop (nothing after this is run)
        if self._is_debug:
            self._app.run(host=self._host, port=self._port, debug=self._is_debug, threaded=is_threaded)
        else:
            # FOR PRODUCTION
            werkzeug.serving.run_simple(
                hostname=self._host,
                port=self._port,
                application=self._app,
                use_debugger=self._is_debug,
                threaded=is_threaded
            )

    def generateRoutes(self):
        """Wrapper around all url route generation"""
        self.createUserPages()
        self.createInfoRoutes()
        self.createMobileRoutes()
        self.createReaderPostRoutes()
        self.createCarRoutes()

    def createInfoRoutes(self):
        """All routes for internal passing of information"""
        @self._app.route("/", methods=["GET"])
        def index():
            return redirect(url_for("api"))

        @self._app.route("/api/info")
        def api():
            """Provides a list of all the possibe api's"""
            routes:List[str] = self.flask_helper.get_links(include_domain=False)
            # dict of {rule type: (box-color, [route_&_methods, ...]), other_rule_types...}
            apis: TypedDict[str, Tuple[str, List[str] ] ] = {
                "reader":   ("is-warning", []),
                "mobile":   ("is-primary", []),
                "cars":     ("is-success", []),
                "api":     ("is-info", []),
                "user":     ("is-danger", []), # for rn, skip user pages as not used
            }

            # classify each type of route w/ style for html
            for rule in routes:
                if "/reader" in rule:   apis["reader"][1].append(rule)
                elif "/mobile" in rule: apis["mobile"][1].append(rule)
                elif "/cars" in rule:   apis["cars"][1].append(rule)
                elif "/api" in rule:    apis["api"][1].append(rule)
                elif "/user" in rule:   apis["user"][1].append(rule)


            return render_template("api.html", title="SpotASpot APIs", apis=apis)

        @self._app.route("/api/info.md", methods=["GET"])
        def api_md():
            return render_template("api.md.html", title="API Info")


    def createReaderPostRoutes(self):
        """All routes for receiving information from the reader's"""
        @self._app.route("/reader/add_reader", methods=["POST"], defaults={'lat': None, 'long':None, 'range':None, 'bearing': None})
        @self._app.route("/reader/add_reader?lat=<lat>&long=<long>&range=<range>&bearing=<bearing>", methods=["POST"])
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
                new_reader_id = self.add_reader(lat, long, range, reader_front_bearing)

            return {
                "new_reader_added": new_reader_id
            }

        @self._app.route("/reader/send_event_data", defaults={'reader_id': -1, 'tag_id': -1, 'signal_strength': -1}, methods=["POST"])
        @self._app.route("/reader/send_event_data?reader_id=<reader_id>&tag_id=<tag_id>&signal_strength=<signal_strength>", methods=["POST"])
        def reader_send_event_data(reader_id, tag_id, signal_strength) -> SendEventDataRes:
            """
            \n:brief Stores the event in the correct database table and ensures the data is processed
            \nParams: reader_id, tag_id, and signal_stregth
            \nTest: curl -X POST "http://localhost:31025/reader/send_event_data?reader_id=2&tag_id=4"
            """
            # Receive + Store data from reader
            args = request.args
            is_valid_arg    = lambda x: x != None and (x != -1 and x != -1.0)
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
            observation_id = self.add_observation_event(readeable_timestamp, signal_strength, reader_id, tag_id)
            if (observation_id == -1):
                # skip detection if there was an error observing
                print(f"Failed: add_observation_event({(readeable_timestamp, signal_strength, reader_id, tag_id)})")
                return invalid_ret

            # run algorithm to see if a detection was made
            detect_res = self.run_detect_algo(observation_id)
            # provide scope for vars and default to already known values
            car_id = detect_res['car_id'] if detect_res else -1
            detect_id = -1
            spot_id = -1

            # fill in rest of return json if car completely detected and have all the info
            if(detect_res != None and detect_res['is_car_parked'] is True):
                # car is detected as parked so mark in db
                detect_car_spot_dict = self.add_detection_and_park_car(
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

    def createMobileRoutes(self):
        """All routes requests from the Mobile App"""

        @self._app.route("/mobile/get_spot_coord/<int:spot_id>", methods=["GET"])
        def get_coord_from_spot_id(spot_id: int):
            """:returns {latitude: float, longitude: float}"""
            return self.get_coord_from_spot_id(spot_id)

        @self._app.route("/mobile/get_is_spot_taken/<int:reader_id>")
        def get_is_spot_taken(reader_id: int) -> bool:
            """Given a reader_id, returns the status of the spots it can reach.
            :return {<spot_id>: <status>, <spot_id>: <status>}"""
            return flask.jsonify(self.is_spot_taken(reader_id))

        @self._app.route("/mobile/get_local_readers", methods=["GET"], defaults={'radius': None, 'latitude': None, 'longitude': None})
        @self._app.route("/mobile/get_local_readers?radius=<radius>&latitude=<latitude>&longitude=<longitude>", methods=["GET"])
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
                return flask.jsonify(self.get_readers_in_radius(center_latitude, center_longitude, radius))
            else:
                return "Parameters are missing\n"

    def createUserPages(self):
        # https://flask-login.readthedocs.io/en/latest/#login-example
        @self._app.route("/user/login", methods=["GET", "POST"])
        def login():
            # dont login if already logged in
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            # TODO: how to validate this way?? -> call functions based on the data??
            is_validated = True

            if request.method == "GET":
                return render_template('login.html', title="SpotASpot Login")
            elif request.method == "POST" and not is_validated:
                # unsuccessful login
                flash("Invalid Username or Password!", "is-danger")
                return render_template('login.html', title="SpotASpot Login")

            elif request.method == "POST":
                # username & pwd must be right at this point, so login
                # https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
                # call loadUser() / @user_loader in userManager.py
                # TODO: Get user id from database??
                user_id = 1
                user = User(user_id)
                login_user(user)

                # two seperate flashes for diff categories
                flash("Successfully logged in!", "is-success")


        @self._app.route("/user/register", methods=["POST"],
                         defaults={'fname': None, 'lname': None, 'username': None, 'pwd': None})
        @self._app.route("/user/register?fname=<fname>&lname=<lname>&username=<username>&pwd=<pwd>", methods=["POST"])
        def register(fname:str, lname:str, username:str, pwd:str):
            args = request.args
            fname = args.get("fname")
            lname = args.get("lname")
            username = args.get("username")
            pwd = args.get("pwd")

            # dont add reader if bad data
            if fname == None or lname == None or username == None or pwd == None:
                add_res = -1
            else:
                add_res = self.add_user(fname, lname, username, pwd)
            return {
                "new_user_id": add_res
            }


        @self._app.route("/user/forgot-password", methods=["POST"])
        def forgotPassword():
            #TODO: make this actually validate
            is_validated = True
            # TODO: get actual data to check who is doing forget password

            if request.method == "POST" and is_validated:
                # actually change a user's login given info is valid/allowed
                self.updatePwd()
                flash("Password Reset Successful", "is-success")
                return redirect(url_for('index'))
            elif request.method == "POST":
                flash("Password Reset Failed", "is-danger")

        @self._app.route("/user/logout", methods=["GET", "POST"])
        @login_required
        def logout():
            logout_user()
            flash("Successfully logged out!", "is-success")
            return redirect(url_for("login"))


    def createCarRoutes(self):
        @self._app.route("/cars/add_tag", methods=["POST"])
        def add_tag():
            """Returns the newly created tag's id"""
            return {"new_tag_id": self.add_tag()}

        @self._app.route("/cars/add_car", methods=["POST"], defaults={
            'user_id': None, 'front_tag': None, 'middle_tag': None, 'rear_tag': None})
        @self._app.route("/cars/add_car?user_id=<user_id>&front_tag=<front_tag>&middle_tag=<middle_tag>&rear_tag=<rear_tag>", methods=["POST"])
        def add_car(user_id: int, front_tag: int, middle_tag: int, rear_tag: int):
            args = request.args
            user_id = args.get("user_id")
            front_tag = args.get("front_tag")
            middle_tag = args.get("middle_tag")
            rear_tag = args.get("rear_tag")

            # dont add reader if bad data
            if user_id == None or front_tag == None or middle_tag == None or rear_tag == None:
                new_car_id = -1
            else:
                new_car_id = self.add_car(user_id, front_tag, middle_tag, rear_tag)

            return {"new_car_id": new_car_id}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Start up a web app GUI for the SpotASpot DB App")
    parser.add_argument(
        "-p", "--port",
        type=int,
        required=False,
        help="The port to run the web app from",
        default=31025
    )

    # defaults debugMode to false (only true if flag exists)
    parser.add_argument(
        "--debugModeOn",
        action="store_true",
        dest="debugMode",
        required=False,
        help="Use debug mode for development environments",
        default=False
    )
    parser.add_argument(
        "--debugModeOff",
        action="store_false",
        dest="debugMode",
        required=False,
        help="Dont use debug mode for production environments",
        default=True
    )

    parser.add_argument(
        "-db_u", "--db_username",
        required=False,
        # sometimes this is also root
        default="capstone",
        dest="db_user",
        help="The username for the Database"
    )

    parser.add_argument(
        "-pwd", "--password",
        required=False, # but if not provided asks for input
        default=None,
        dest="pwd",
        help="The password for the Database"
    )
    parser.add_argument(
        "-d", "--db",
        required=False,
        default="SpotASpot",
        dest="db",
        help="The name of the database to connect to"
    )

    parser.add_argument(
        "-dev", "--dev_db",
        required=False,
        action="store_const",
        const="SpotASpot_dev",
        dest="db",
        help="Sets the name of the database to connect to as the dev database"
    )

    parser.add_argument(
        "-dbh", "--database_host",
        required=False,
        default="localhost",
        dest="db_host",
        help="Set the host ip address of the database (can be localhost)"
    )

    # Actually Parse Flags (turn into dictionary)
    args = vars(parser.parse_args())

    # ask for input if password not given
    if args["pwd"] == None:
        pass_msg = "Enter the password for user '"
        pass_msg += str(args["db_user"])
        pass_msg += "' for the database '"
        pass_msg += str(args["db"])
        pass_msg += "': "
        args["pwd"] = getpass.getpass(pass_msg)

    # start app
    app = WebApp(args["port"], args["debugMode"], args["db_user"], args["pwd"], args["db"], args["db_host"])
