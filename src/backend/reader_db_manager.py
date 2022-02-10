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

    def add_reader_event(self,
                            observation_time: str,
                            signal_strength: float,
                            reader_id: int,
                            tag_id: int) -> Optional[Dict]:
        """Adds an observation & detection event.
        Return the generated id for that row in the Observation Table and Detection Table
        \n    observation_time (datetime.strftime):
            The timestamp of receiving that event from the reader in '%Y-%m-%d %H:%M:%S' form
        \n    signal_strength (float):
        \nReturns:
        \n    Dict: {'created_observ_id': <val>, 'created_detect_id': <val>}
        """
        ids_dict = {'created_observ_id': None , 'created_detect_id': None }
        try:
            self.cursor.execute("call add_reader_event(%s, %s, %s, %s)",
                                (observation_time, signal_strength,
                                reader_id, tag_id ))
            ids_dict = self.cursor.fetchall()
            return ids_dict
        except:
            return ids_dict

    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
