#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os, sys
import argparse # cli paths
import logging # used to disable printing of each POST/GET request
from pathlib import Path
import secrets
import getpass
from typing import TypedDict, List, Tuple

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import werkzeug.serving # needed to make production worthy app that's secure

#--------------------------------Project Includes--------------------------------#
from flask_helpers import FlaskHelper, flash_print, is_json, is_form, is_static_req, clear_flashes
from userManager import UserManager
from userRoutes import UserRoutes
from mobileRoutes import MobileRoutes
from readerRoutes import ReaderRoutes
from carRoutes import CarRoutes

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
        self.createHelperRoutes()
        # to provide UserManager & DB_manager, use self which is a child of it
        self.user_routes = UserRoutes(self._app, self)
        self.createInfoRoutes()
        self.mobile_routes = MobileRoutes(self._app, self)
        self.reader_routes = ReaderRoutes(self._app, self)
        self.car_routes = CarRoutes(self._app, self)

    def createHelperRoutes(self):
        @self._app.before_request
        def log_request():
            # traditional place to refresh database connection
            # self.check_conn()

            if is_static_req(request): return None
            print("Request ({0}): {1} -- {2}".format(
                request.remote_addr,
                request,
                request.form if is_form(request) else ""
            ))
            return None

        @self._app.after_request
        def log_response(response):
            if is_static_req(request): return response

            res = response.data
            # check if is binary data
            try:
                res = res.decode()
            except (UnicodeDecodeError, AttributeError):
                pass

            # if is json, dont print data
            is_json(res)

            print("Response ({0}) {1}: {2}".format(
                request.remote_addr,
                response,
                # assume all return data is json format
                res.strip() if is_json(res) else ""
            ))
            return response

    def createInfoRoutes(self):
        """All routes for internal passing of information"""
        @self._app.route("/", methods=["GET"])
        @self._app.route("/index", methods=["GET"])
        def index():
            return redirect(url_for("api"))

        @self._app.route("/api/info")
        def api():
            """Provides a list of all the possibe api's"""
            routes:List[str] = self.flask_helper.get_links(include_domain=False)
            # dict of {rule type: (box-color, [route_&_methods, ...]), other_rule_types...}
            apis: TypedDict[str, Tuple[str, List[str] ] ] = {
                "reader":   ("is-link", []),
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
