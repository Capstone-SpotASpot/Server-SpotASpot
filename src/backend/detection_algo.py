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

class DetectionAlgo():
    def __init__(self, conn: pymysql.Connection, cursor: Cursor) -> None:
        """
            @brief: Used to implement the algo to detect if a car was detected.
        """
        self.conn = conn
        self.cursor = cursor

    def cmp_observ_ev(self, observ_id):
        try:
            print(f"proc observ_id = {observ_id}")
            self.cursor.execute("call cmp_observ_ev(%s)", (observ_id))
            cmp_observ_res = list(self.cursor.fetchall())
            print(f"cmp_observ_res={cmp_observ_res}")
            # return raw_res[0]["created_user_id"]
        except Exception as err:
            print(f"cmp_observ_ev() error: {err}")
            return -1


    def run_detect_algo(self, observ_id) -> Dict[str, int]:
        """If the observ_id leads to detection of parked car, return necessary info for add_detection()"""
        # TODO: call db procedure for detection algo
        self.cmp_observ_ev(observ_id)
        print(f"")

        # mark some observation events as not relevent if detection is true and switched

        # TODO: Should 3 events be necessary? Should 2 be minimum and make third Null
        reader_id = None
        observation1_id = None
        observation2_id = None
        observation3_id = None
        return {
            "reader_id": reader_id,
            "observation1_id": observation1_id,
            "observation2_id": observation2_id,
            "observation3_id": observation3_id
        }

    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
