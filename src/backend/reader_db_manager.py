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
                            signal_strength: float) -> Optional[int]:
        """Adds an observation event and return the generated id for that row in the table
        \n    observation_time (datetime.strftime):
            The timestamp of receiving that event from the reader in '%Y-%m-%d %H:%M:%S' form
        \n    signal_strength (float):
        \nReturns:
        \n    int: The id of the event stored in the DB. None on failure
        """
        print(f"\nobservation_time = {observation_time}, signal_strength = {signal_strength}")
        try:
            self.cursor.execute("call add_observation_event(%s, %s)",
                                (observation_time, signal_strength))
            observ_id = self.cursor.fetchall()[0]
            return observ_id
        except:
            return None




    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
