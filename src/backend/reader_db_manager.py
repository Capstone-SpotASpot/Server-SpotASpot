#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os
import sys
from typing import Optional, Dict, List
from datetime import datetime

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql
from pymysql import connections, cursors
from pymysql.cursors import Cursor

class ReaderDBManager():
    def __init__(self, conn: pymysql.Connection, cursor: Cursor, db_start_cb) -> None:
        """
            @brief: Used to implement all database management for the reader's specifically.
            @args
                db_start_cb - function to call prior to any db actions
        """
        self.conn = conn
        self.cursor = cursor
        self.db_start_cb = db_start_cb

    def get_coord_from_spot_id(self, spot_id: int) -> Dict[str, float]:
        """:returns {latitude: float, longitude: float}"""
        self.db_start_cb()
        try:
            self.cursor.execute("call get_coord_from_spot_id(%s)", (spot_id))

            coord_res = list(self.cursor.fetchall())[0]
            if 'Level' in coord_res and observ_res['Level'] == "Error":
                print(f"mysql add_observation_event() err: {coord_res}")
                return -1

            # dict of two elements (lat & long) and can just return
            return coord_res
        except Exception as err:
            print(f"add_observation_event() error: {err})")
            return -1

    def add_observation_event(self,
                            observation_time: str,
                            signal_strength: float,
                            reader_id: int,
                            tag_id: int) -> Optional[int]:
        """Adds an observation & detection event.
        Return the generated id for that row in the Observation Table and Detection Table
        \n    observation_time (datetime.strftime):
            The timestamp of receiving that event from the reader in '%Y-%m-%d %H:%M:%S' form
        \n    signal_strength (float):
        \nReturns: The observation id (-1 if error)
        """
        self.db_start_cb()
        observ_id = -1
        try:
            self.cursor.execute("call add_observation(%s, %s, %s, %s)",
                (observation_time, signal_strength, reader_id, tag_id))

            observ_res = list(self.cursor.fetchall())[0]
            if 'Level' in observ_res and observ_res['Level'] == "Error":
                print(f"mysql add_observation_event() err: {observ_res}")
                return -1
            # dict of one element & only care about value
            observ_id = list(observ_res.values())[0]
            return int(observ_id)
        except Exception as err:
            print(f"add_observation_event() error: {err} (observ_id={observ_id})")
            return -1

    def add_detection_and_park_car(self,
                      reader_id,
                      observation1_id,
                      observation2_id,
                      observation3_id) -> Optional[Dict]:
        """Dict keys: created_detect_id, parked_car_id, parked_spot_id"""
        self.db_start_cb()
        try:
            self.cursor.execute("call add_detection_and_park_car(%s, %s, %s, %s)",
                (reader_id, observation1_id, observation2_id, observation3_id))

            # should only return 1 row of info & not have {'Level': "Error"}
            detect_car_spot_dict = list(self.cursor.fetchall())[0]
            if 'Level' in detect_car_spot_dict and detect_car_spot_dict['Level'] == "Error":
                print(f"add_detection_and_park_car() err: {detect_car_spot_dict}")
                return None
            return detect_car_spot_dict
        except Exception as err:
            print(f"add_detection_and_park_car() err: {err}")
            return None

    def reader_cleanup(self):
        self.db_start_cb()
        self.cursor.close()
        self.conn.close()
