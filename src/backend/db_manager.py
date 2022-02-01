#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os, sys
import argparse # cli paths
import datetime
from typing import Optional, Dict, List

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql

#--------------------------------Project Includes--------------------------------#
from reader_db_manager import ReaderDBManager
from mobile_app_db_manager import MobileAppDBManager


class DB_Manager(ReaderDBManager, MobileAppDBManager):
    def __init__(self, user:str, pwd:str, db:str, host:str):
        """
            \n@param: user  - The username to connect to database with
            \n@param: pwd   - The password to connect to database with
            \n@param: db    - The name of the database to connect with
            \n@param: host  - The IP/localhost of the database to connect with
        """
        try:
            self.conn = pymysql.connect(
                host=host,
                user=user,
                password=pwd,
                db=db,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
        except Exception as err:
            raise SystemExit(f"Invalid Database Login: {err}")

        ReaderDBManager.__init__(self, user, pwd, db, host)
        MobileAppDBManager.__init__(self, user, pwd, db, host)

    def cleanup(self):
        self.cursor.close()
        self.conn.close()

        # Clean up all DB Managers
        self.reader_cleanup()
        self.mobile_app_cleanup()

    def add_user(self):
        "Function to add a user. Right now it does nothing"
        return 1

    def updatePwd(self):
        "WIP"
        pass

if __name__ == '__main__':
    # TODO: change this name
    parser = argparse.ArgumentParser(description="Library Database Python Connector")
    parser.add_argument(
        "-u", "--username",
        required=False,
        default="root",
        dest="user",
        help="The username for the MySQL Database"
    )

    parser.add_argument(
        "-pwd", "--password",
        required=True,
        default=None,
        dest="pwd",
        help="The password for the MySQL Database"
    )

    parser.add_argument(
        "-d", "--db",
        required=False,
        # TODO: change this name
        default="libsystem",
        dest="db_name",
        help="The name of the database to connect to"
    )


    # actually parse args (convert to dict form)
    args = vars(parser.parse_args())

    # make the object
    db = DB_Manager(args["user"], args["pwd"], args["db_name"])
