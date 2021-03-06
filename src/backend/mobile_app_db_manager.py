#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from csv import reader
import os
import sys
from typing import Optional, Dict, List
from xmlrpc.client import Boolean

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql
from pymysql import connections, cursors
from pymysql.cursors import Cursor

#--------------------------------Project Includes--------------------------------#

class MobileAppDBManager():
    def __init__(self, conn: pymysql.Connection, cursor: Cursor, db_start_cb) -> None:
        """
            @brief: Used to implement all database management for the Mobile App to get info.
            @args
                db_start_cb - function to call prior to any db actions
        """
        self.conn = conn
        self.cursor = cursor
        self.db_start_cb = db_start_cb

    def add_user(self, first_name, last_name, username, pwd)-> bool:
        """Function to add a user
        \n:Return: True if add success, False otherwise """
        self.db_start_cb()
        try:
            self.cursor.execute("call add_user(%s, %s, %s, %s)",
                                (first_name, last_name, username, pwd))
            raw_res = list(self.cursor.fetchall())
            return raw_res[0]["created_user_id"]
        except Exception as err:
            return -1

    def is_spot_taken(self, reader_id: int) -> Optional[Dict]:
        """Given the reader's unique id, return if its spots are taken or not.
        <status> = True if taken, False if empty/not-taken
        \nNote: for testing, status: 0 = free, 1 = taken, -1 = something else
        \n@return:
            \n\t None = reader_id does not exist
            \n\t {<spot_id>: {'status': <status>, ...}}
        """
        # TODO: maybe change this to spot id and not reader_id??
        self.db_start_cb()
        try:
            if(not self.does_reader_exist(reader_id)):
                return { int(reader_id): {
                    'error': "reader does not exist"
                }}

            self.cursor.execute("call is_spot_taken(%s)", reader_id)
            # form:  [{spot_id, longitude, latitude, status}]
            raw_status_dict = self.cursor.fetchall()

            # Transform dict to match return expected
            status_dict = {}
            for row in raw_status_dict:
                # spot_status = 0 on not taken, 1 on taken, -1 on other
                # print("row['spot_status'] = {}".format(row['spot_status']))
                is_spot_taken = None
                if row['spot_status'] == 0:
                    is_spot_taken = False
                elif row['spot_status'] == 1:
                    is_spot_taken = True

                status_dict[int(row['spot_id'])] = {
                    'is_spot_taken': is_spot_taken,
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'parked_car': row['parked_car_id']
                }

            return status_dict
        except Exception as err:
            print(f"is_spot_taken error: {err}")
            return None

    def does_reader_exist(self, reader_id: int) -> bool:
        self.db_start_cb()
        try:
            self.cursor.execute("select does_reader_exist(%s)", (reader_id))
            return list(self.cursor.fetchone().values())[0]
        except Exception as err:
            print(f"does_reader_exist() err: {err}")
            return False

    def calc_coord_dist(self, lat1: float, long1: float, lat2: float, long2: float) -> float:
        self.db_start_cb()
        try:
            self.cursor.execute("select calc_coord_dist(%s, %s, %s, %s)",
                                (lat1, long1,
                                 lat2, long2))
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"calc_coord_dist error: {err}")
            return -1

    def get_readers_in_radius(self, center_latitude: float, center_longitude: float, radius: float) -> Optional[List[Dict]]:
        """Given a set of coordinates, finds all readers with a given GPS distance (radius) from that point """
        self.db_start_cb()
        try:
            self.cursor.execute("call get_readers_in_radius(%s, %s, %s)",
                                (center_latitude, center_longitude, radius))
            readers_in_range_dict = self.cursor.fetchall()
            return readers_in_range_dict

        except Exception as err:
            print(f"get_readers_in_radius error: {err}")
            return None


    def add_car(self,
        user_id: int,
        tag_id_front: int,
        tag_id_middle: int,
        tag_id_rear: int
    ):
        """Add a user's car to the database giventheir car's 3 tags & their id
        Returns: The created car's id (-1 if error)
        """
        self.db_start_cb()
        try:
            self.cursor.execute("call add_car(%s, %s, %s, %s)",
                (user_id, tag_id_front, tag_id_middle, tag_id_rear))
            # ignore name of field and just get the value
            raw_res = list(self.cursor.fetchall())
            return int(raw_res[0]["created_car_id"])
        except Exception as err:
            return -1

