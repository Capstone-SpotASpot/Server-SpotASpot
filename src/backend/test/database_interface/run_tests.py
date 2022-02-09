#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from msilib.schema import Class
from sqlite3 import Cursor
import unittest
import pymysql
import getpass
import os
import sys
import logging  # used to disable printing of each POST/GET request
import pathlib
from pathlib import Path
import secrets
import typing
from typing import Dict

# Change this to have project includes
sys.path.insert(0, os.path.abspath("../../"))

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#

#--------------------------------Project Includes--------------------------------#
from test_reader import TestReader
from test_user import TestUser

from cli_parser import CLIParser
from db_manager import DB_Manager

class ConnectionMaker(unittest.TestCase):
    def __init__(self, parsed_args: Dict):
        self.args = parsed_args
        self.db_manager = DB_Manager(self.args['db_user'], self.args['pwd'],
                                     self.args['db'], self.args['db_host'])
        self.conn = self.db_manager.conn
        self.cursor = self.db_manager.cursor



if __name__ == '__main__':
    valid_tests = {
        "ALL": "ALL",
        "add_reader": TestReader,
        "add_user": TestUser
    }
    parser = CLIParser(valid_tests)
    made_conn = ConnectionMaker(parser.args)
    conn = made_conn.conn
    cursor = made_conn.cursor

    # Get around unittest's inability to pass args to setUp()
    # By setting the class variables for EACH test case class to have the connection
    # ONLY way to pass DB connections to test cases due to unittest's design
    TestUser.setUpConn(made_conn.db_manager)
    TestReader.setUpConn(made_conn.db_manager)

    # Find the desired test list
    tests_to_run = []
    test_list = parser.args['test']
    if 'ALL' in test_list:
        print("Running all tests")
        print("-------------------------------------\n\n")
        del valid_tests["ALL"]
        for classname_str in list(valid_tests.values()):
            tests_to_run.append(classname_str)
    else:
        # All cb's take db_manager obj as a param
        for test_selected in test_list:
            tests_to_run.append(valid_tests[test_selected])

    # setup testing
    suite = unittest.TestSuite()
    for test in tests_to_run:
        suite.addTest(unittest.makeSuite(test))

    unittest.TextTestRunner(verbosity=2).run(suite)
