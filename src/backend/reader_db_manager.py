#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os
import sys
from typing import Optional, Dict, List

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

    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
