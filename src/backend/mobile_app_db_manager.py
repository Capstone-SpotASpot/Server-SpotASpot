#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from csv import reader
import os
import sys
from typing import Optional, Dict, List
from xmlrpc.client import Boolean

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql

#--------------------------------Project Includes--------------------------------#
from gps import GPS

class MobileAppDBManager():
    def __init__(self, user: str, pwd: str, db: str, host: str) -> None:
        """
            @brief: Used to implement all database management for the Mobile App to get info.
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

    def mobile_app_cleanup(self):
        self.cursor.close()
        self.conn.close()

    def is_reader_taken(self, reader_id: int) -> Optional[bool]:
        """Given the reader's unique id, return if its spot is taken or not.
        \nNote: for testing, reader 0 = free, reader 1 = taken.
        \n@return:
            \n\t None = reader_id does not exist
            \n\t True = reader's spot is not free/taken
            \n\t False = reader's spot is free
        """
        # TODO: actually implement this
        if reader_id == 0:
            return False
        elif reader_id == 1:
            return True
        else:
            return None

    def get_readers_in_radius(self, x_coord: float, y_coord: float, radius: float) -> List[Dict]:
        """Given a set of coordinates, finds all readers with a given GPS distance (radius) from that point """
        # TODO: ask the database for all the readers
        readers_from_db = [{'id': 1, "x": 1, "y": 1},
                         {'id': 2, "x": 10, "y": 5}
                        ]
        valid_reader_dict = []
        for reader in readers_from_db:
            if GPS.is_in_range(x_coord, y_coord, reader['x'], reader['y'], radius):
                valid_reader_dict.append(reader)
        return valid_reader_dict



