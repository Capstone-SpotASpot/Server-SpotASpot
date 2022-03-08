#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os
import sys
from typing import Optional, Dict, List
from datetime import datetime
from typing import TypedDict

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql
from pymysql import connections, cursors
from pymysql.cursors import Cursor

class DetectAlgoRes(TypedDict):
    reader_id: int
    observation1_id: int
    observation2_id: Optional[int]
    observation3_id: Optional[int]
    is_car_parked: bool
    car_id: int

class DetectionAlgo():
    def __init__(self, conn: pymysql.Connection, cursor: Cursor, db_start_cb) -> None:
        """
            @brief: Used to implement the algo to detect if a car was detected.
            @args
                db_start_cb - function to call prior to any db actions
        """
        self.conn = conn
        self.cursor = cursor
        self.db_start_cb = db_start_cb

    def cmp_observ_ev(self, observ_id):
        """:return reader_id, car_id, is_car_parked, observation_id"""
        self.db_start_cb()
        try:
            self.cursor.execute("call cmp_observ_ev(%s)", (observ_id))
            cmp_observ_res = list(self.cursor.fetchall())[0]
            if 'Level' in cmp_observ_res and cmp_observ_res['Level'] == "Error":
                print(f"cmp_observ_ev() err: {cmp_observ_res}")
                return None
            return cmp_observ_res
        except Exception as err:
            print(f"cmp_observ_ev() error: {err}")
            return None

    def get_observ_id_from_parked_car(self, car_id_in: int) -> Optional[List[Dict]]:
        """:return a 2-3 row dict containing <tag_id, observ_id> that resulted in the algo calling this car parked"""
        self.db_start_cb()
        try:
            self.cursor.execute("call get_observ_id_from_parked_car(%s)", (car_id_in))
            raw_ids = self.cursor.fetchall()
            return raw_ids
        except Exception as err:
            print(f"get_observ_id_from_parked_car() err: {err}")
            return None

    def run_detect_algo(self, observ_id) -> DetectAlgoRes:
        """If the observ_id leads to detection of parked car, return necessary info for add_detection_and_park_car()
        \n:return dict of {reader_id, observation1_id, observation2_id, observation3_id, is_car_parked, car_id}.
        \n:Note: the observation id's could be null.
        \n:CHECK IF CAR PARKED: use the `is_car_parked` field"""
        # TODO: Call DB procedure to see if car with THIS tag is ALREADY parked in THIS reader's spot
        # "is this tag on a car that is ALREADY parked in this spot"
        # IF yes -> update detection to include this new observation
        #   OR can ignore this observation and NOT start a new potential detection / mark this reading as irrelevant
        self.db_start_cb()

        # get ( reader_id, car_id, is_car_parked, observation_id)
        cmp_observ_dict = self.cmp_observ_ev(observ_id)
        if cmp_observ_dict == None: return None

        # true if db sees >=2 of the car's tags in the same spot
        is_car_parked = True if cmp_observ_dict['is_car_parked'] == 1 else 0
        detection_components_dict : DetectAlgoRes = {
            "reader_id": cmp_observ_dict['reader_id'],
            "observation1_id": observ_id,
            "observation2_id": None,
            "observation3_id": None,
            "is_car_parked": is_car_parked,
            "car_id": cmp_observ_dict['car_id']
        }

        if is_car_parked is True:
            # get the observation id's responsible for the new decision that the car is parked
            tag_observe_id_list = self.get_observ_id_from_parked_car(cmp_observ_dict['car_id'])
            for idx, tag_observe_pair in enumerate(tag_observe_id_list, start=0):
                # map potential row's of observations to the detection dict
                if idx % 3 == 0:
                    detection_components_dict['observation1_id'] = tag_observe_pair['observ_id']
                elif idx % 3 == 1:
                    detection_components_dict['observation2_id'] = tag_observe_pair['observ_id']
                elif idx % 3 == 2:
                    detection_components_dict['observation3_id'] = tag_observe_pair['observ_id']

        return detection_components_dict

    def reader_cleanup(self):
        self.db_start_cb()
        self.cursor.close()
        self.conn.close()
