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
    def __init__(self, conn: pymysql.Connection, cursor: Cursor) -> None:
        """
            @brief: Used to implement all database management for the reader's specifically.
        """
        self.conn = conn
        self.cursor = cursor

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
        \nReturns: The observation id
        """
        try:
            self.cursor.execute("call add_observation(%s, %s, %s, %s)",
                                (observation_time, signal_strength,
                                reader_id, tag_id ))
            raw_id = list(self.cursor.fetchall().values())[0]
            return int(raw_id)
        except:
            return None

    def add_detection(self,
                      reader_id,
                      observation1_id,
                      observation2_id,
                      observation3_id) -> Optional[Dict]:
        try:
            self.cursor.execute("call add_detection(%s, %s, %s, %s)",
                                (reader_id, observation1_id,
                                 observation2_id, observation3_id))
            raw_id = list(self.cursor.fetchall().values())[0]
            return int(raw_id)
        except:
            return None

    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
