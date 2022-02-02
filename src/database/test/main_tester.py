#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import getpass
import os
import sys
import logging  # used to disable printing of each POST/GET request
import pathlib
from pathlib import Path
import secrets

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql


#--------------------------------Project Includes--------------------------------#
from cli_setup import CLISetup
from test_add_user import test_add_user

class MainTester(CLISetup):
    def __init__(self):
        """Basic class to setup testing sql files. Will handle establishing a connection to the test database"""
        self.valid_tests = {
            "ALL" : "ALL",
            "add_user": test_add_user
        }
        super().__init__(self.valid_tests)

        try:
            self.conn = pymysql.connect(
                host=self.args['db_host'],
                user=self.args['db_user'],
                password=self.args['pwd'],
                db=self.args['db'],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
        except Exception as err:
            raise SystemExit(f"Invalid Database Login: {err}")
        if self.args['test'] == "ALL":
            print("Running all tests")
        else:
            print("Running test: " + self.args['test'] + ".py")

            # All cb's take connection and cursor as params
            test_func_cb = self.valid_tests[self.args['test']]
            test_func_cb(self.conn, self.cursor)

        # Close all connnections
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    MainTester()


