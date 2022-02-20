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

class WebApp(UserManager):
    def __init__(self, port: int, is_debug: bool, user: str, pwd: str, db: str, db_host: str):
        self._app = Flask("SpotASpot_ServerApp")
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True # refreshes flask if html files change
        self._app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

        # Inheret all functions and 'self' variables (UserManager)
        UserManager.__init__(self, self._app, user, pwd, db, db_host)
        self.flask_helper = FlaskHelper(self._app, port)

        # current dir
        backend_dir = Path(__file__).parent.resolve()
        src_dir = backend_dir.parent

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
        self.createMobileGetRoutes()
        self.createReaderPostRoutes()
        self.createTagRoutes()

    def createInfoRoutes(self):
        """All routes for internal passing of information"""
        pass

    def createReaderPostRoutes(self):
        """All routes for receiving information from the reader's"""
        @self._app.route("/reader/send_event_data",
                        methods=["POST"],
                        defaults={'reader_id': -1, 'tag_id': -1, 'signal_strength': -1})
        def reader_send_event_data(reader_id: int, tag_id: int, signal_strength: float) -> dict:
            """
            \n:brief Stores the event in the correct database table and ensures the data is processed
            \nParams: reader_id, tag_id, and signal_stregth
            \nTest: curl -X POST "http://localhost:31025/reader/send_event_data?reader_id=2&tag_id=4"
            """
            # Receive + Store data from reader
            args = request.args
            reader_id = args.get('reader_id')
            tag_id = args.get('tag_id')
            signal_strength = args.get('signal_strength') if args.get('signal_strength') != None else -1
            timestamp = datetime.now()
            readeable_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            observation_id = self.add_observation_event(
                readeable_timestamp, signal_strength, reader_id, tag_id)

            # skip detection if there was an error observing
            detect_id = None
            if (observation_id != -1):
                # run algorithm to see if a detection was made
                detect_res = self.run_detect_algo(observation_id)
                print(f"reader_id={reader_id}, tag_id={tag_id} -> observation_id={observation_id}")
                print(f"detect_res={detect_res}")

                # TODO: if needed, call add_detection()
                if(detect_res):
                    detect_car_spot_dict = self.add_detection(**detect_res)
                    detect_id = detect_car_spot_dict['created_detect_id']
                    spot_id = detect_car_spot_dict['parked_spot_id']
                    car_id = detect_car_spot_dict['parked_car_id']

            # TODO: add more fields like, car_id, spot_id, and other useful info to update app
            return {
                "new_car_detected": detect_id != None
            }

    def createMobileGetRoutes(self):
        """All routes for Get requests from the Mobile App"""
        @self._app.route("/mobile/get_is_spot_taken/<int:reader_id>")
        def get_is_spot_taken(reader_id: int) -> bool:
            """Given a reader_id, returns the status of the spots it can reach.
            :return {<spot_id>: <status>, <spot_id>: <status>}"""
            return flask.jsonify(self.is_spot_taken(reader_id))

        @self._app.route("/mobile/get_local_readers",
                        methods=["GET"],
                        defaults={'radius': None, 'x_coord': None, 'y_coord': None})
        def get_local_readers(radius: float, x_coord: float, y_coord: float):
            args = request.args
            radius = float(args.get('radius')) if args.get('radius') is not None else None
            x_coord = float(args.get('x_coord')) if args.get('x_coord') is not None else None
            y_coord = float(args.get('y_coord')) if args.get('y_coord') is not None else None
            """Given GPS coordiantes and a radius,
            returns a list of dictionaries containing all readers in that radius"""
            # if the request is not fully formed, do not accept it
            if radius is not None and x_coord is not None and y_coord is not None:
                # only return the reader's id and their gps coords that match
                return flask.jsonify(self.get_readers_in_radius(x_coord, y_coord, radius))
            else:
                return "Parameters are missing\n"

    def createUserPages(self):
        # https://flask-login.readthedocs.io/en/latest/#login-example
        @self._app.route("/login", methods=["GET", "POST"])
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

            # # route to original destination
            # next = flask.request.args.get('next')
            # isNextUrlBad = next == None or not is_safe_url(next, self._urls)
            # if isNextUrlBad:
            #     return redirect(url_for('index'))
            # else:
            #     return redirect(next)

            # # on error, keep trying to login until correct
            # return redirect(url_for("login"))

        @self._app.route("/register", methods=["POST"])
        def register():
            # TODO: figure out how to do form/validation???
            is_validated = True
            if current_user.is_authenticated: return redirect(url_for('index'))
            elif request.method == "POST" and is_validated:
                # TODO: make a db_manager function for adding a user
                add_res = self.addUser()

                if (add_res == -1):
                    flash("Username already taken", "is-danger")
                elif (add_res == 1):
                    msg = "Congratulations, you are now a registered user!"
                    flash(msg, " is-success")
                elif (add_res == 0):
                    flash('Registration Failed!', "is-danger")

                # since form validated, always return to login
                return redirect(url_for("login"))

            elif request.method == "POST":
                print("Registration Validation Failed")

        @self._app.route("/forgot-password", methods=["POST"])
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

        @self._app.route("/logout", methods=["GET", "POST"])
        @login_required
        def logout():
            logout_user()
            flash("Successfully logged out!", "is-success")
            return redirect(url_for("login"))


    def createTagRoutes(self):
        @self._app.route("/tags/add_tag", methods=["GET"])
        def add_tag():
            """Returns the newly created tag's id"""
            return {"new_tag_id": self.add_tag()}

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
