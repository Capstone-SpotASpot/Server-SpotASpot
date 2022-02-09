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
            \nNote: This class defines all functions not specific to the Reader or Mobile App
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

        ReaderDBManager.__init__(self, self.conn, self.cursor)
        MobileAppDBManager.__init__(self, self.conn, self.cursor)

    def cleanup(self):
        self.cursor.close()
        self.conn.close()

    def updatePwd(self):
        "WIP"
        pass

    def add_reader(self, latitude: float, longitude: float, reader_range: float) -> int:
        """Add a reader to the database.
        \n reader_range is the radius of the readers range in meters(m)
        \n:return the added reader's id if added successfully. -1 if error."""
        try:
            self.cursor.execute("call add_reader(%s, %s, %s)",
                                (latitude, longitude, reader_range))
            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_reader error: {err}")
            return -1

    def add_tag(self) -> int:
        """Creates a new database entry for a single tag and returns its unique id.

        Returns:
            int: The id of the newly created tag (-1 if error)
        """
        try:
            self.cursor.execute("call add_tag()")
            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_tag error: {err}")
            return -1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Database Python Connector")
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
        default="SpotASpot",
        dest="db_name",
        help="The name of the database to connect to"
    )


    # actually parse args (convert to dict form)
    args = vars(parser.parse_args())

    # make the object
    db = DB_Manager(args["user"], args["pwd"], args["db_name"])
