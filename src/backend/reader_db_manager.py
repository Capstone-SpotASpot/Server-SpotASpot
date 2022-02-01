#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os
import sys
from typing import Optional, Dict, List

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql


class ReaderDBManager():
    def __init__(self, user: str, pwd: str, db: str, host: str) -> None:
        """
            @brief: Used to implement all database management for the reader's specifically.
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

    def reader_cleanup(self):
        self.cursor.close()
        self.conn.close()
