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
from detection_algo import DetectionAlgo

class DB_Manager(ReaderDBManager, MobileAppDBManager, DetectionAlgo):
    def __init__(self, user:str, pwd:str, db:str, host:str):
        """
            \n@param: user  - The username to connect to database with
            \n@param: pwd   - The password to connect to database with
            \n@param: db    - The name of the database to connect with
            \n@param: host  - The IP/localhost of the database to connect with
            \nNote: This class defines all functions not specific to the Reader or Mobile App
        """
        self._host = host
        self._user = user
        self._pwd = pwd
        self._db = db
        try:
            self.connect_db()
        except Exception as err:
            raise SystemExit(f"Invalid Database Login: {err}")

        ReaderDBManager.__init__(self, self.conn, self.cursor, self.check_conn)
        MobileAppDBManager.__init__(self, self.conn, self.cursor, self.check_conn)
        DetectionAlgo.__init__(self, self.conn, self.cursor, self.check_conn)

    def connect_db(self):
        """Creates self.conn & self.cursor objects"""
        self.conn = pymysql.connect(
            host=self._host,
            user=self._user,
            password=self._pwd,
            db=self._db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def cleanup(self):
        self.cursor.close()
        self.conn.close()

    def check_conn(self):
        """Decorator to check if need to reconnect to db & does so if needed"""
        # check if youre connected, if not, connect again
        self.conn.ping(reconnect=True)
        self.cursor = self.conn.cursor()

    def updatePwd(self):
        "WIP"
        pass

    def add_reader(self, latitude: float, longitude: float, reader_range: float, reader_front_bearing: float) -> int:
        """Add a reader to the database.
        \n reader_range is the radius of the readers range in meters(m)
        \n reader_front_bearing is the direction the reader is facing (in degrees) relative to true north.
            This can be obtained via the compass app on a phone, google maps, etc...
            while standing near the reader in the direction it faces
        \n:return the added reader's id if added successfully. -1 if error."""
        self.check_conn()
        try:
            self.cursor.execute("call add_reader(%s, %s, %s, %s)",
                                (latitude, longitude, reader_range, reader_front_bearing))
            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_reader error: {err}")
            return -1

    def add_tag(self, new_tag_id: int) -> int:
        """Creates a new database entry for a single tag and returns its unique id.
        Params:
            new_tag_id: The id of the tag being added
        Returns:
            int: The id of the newly created tag (-1 if error)
        """
        self.check_conn()
        try:
            self.cursor.execute("call add_tag(%s)", new_tag_id)
            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_tag error: {err}")
            return -1

    def add_car(self, user_id: int, front_tag: int, middle_tag: int, rear_tag: int) -> int:
        """Creates a new database entry for a car and returns its unique id.

        Returns:
            int: The id of the newly created car (-1 if error)
        """
        self.check_conn()
        try:
            self.cursor.execute("call add_car(%s, %s, %s, %s)",
                (user_id, front_tag, middle_tag, rear_tag))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_car error: {err}")
            return -1

    def add_user(self, fname:str, lname:str, username:str, pwd:str) -> int:
        """Creates a new database entry for a user and returns its unique id.

        Returns:
            int: The id of the newly created user (-1 if error)
        """
        self.check_conn()
        try:
            self.cursor.execute("call add_user(%s, %s, %s, %s)",
                (fname, lname, username, pwd))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_car error: {err}")
            return -1

    def does_username_exist(self, uname: str) -> bool:
        self.check_conn()
        try:
            self.cursor.execute("call does_username_exist(%s)", (uname))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"does_username_exist error: {err}")
            return -1

    def get_user_id(self, uname) -> int:
        """:returns the user_id of user with 'username' (-1 on error)"""
        self.check_conn()
        try:
            self.cursor.execute("select get_user_id(%s)", uname)
            user_ids = list(self.cursor.fetchone().values())[0]
            # use '.values()' to make python agnostic to the name of returned col in procedure
            # return user_ids[0].values()[0] if len(user_ids) > 0 else -1
            return user_ids if user_ids is not None else -1
        except:
            return -1

    def update_pwd(self, uname: str, pwd: str) -> bool:
        """:returns -1 on error, 1 on success"""
        self.check_conn()
        try:
            self.cursor.execute("call update_pwd(%s, %s)", (uname, pwd))

            # ignore name of field and just get the value
            return 1
        except Exception as err:
            print(f"update_pwd error: {err}")
            return -1

    def check_password(self, uname: str, pwd: str) -> bool:
        """Returns True if password and username are valid to login"""
        self.check_conn()
        try:
            self.cursor.execute("call check_password(%s, %s)", (uname, pwd))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"check_password error: {err}")
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
