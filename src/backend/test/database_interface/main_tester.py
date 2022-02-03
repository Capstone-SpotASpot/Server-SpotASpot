#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import getpass
import os
import sys
import logging  # used to disable printing of each POST/GET request
import pathlib
from pathlib import Path
import secrets
# Change this to have project includes
sys.path.insert(0, os.path.abspath("../../"))

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql


#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager
from cli_parser import CLIParser
from test_add_user import test_add_user


class MainTester(CLIParser):
    def __init__(self):
        """Basic class to setup testing sql files. Will handle establishing a connection to the test database"""
        self.valid_tests = {
            "ALL" : "ALL",
            "add_user": test_add_user
        }

        # Init CLI first, then DBManager
        CLIParser.__init__(self, self.valid_tests)

        self.db_manager = DB_Manager(self.args['db_user'], self.args['pwd'],
                                self.args['db'], self.args['db_host'])

        if self.args['test'] == "ALL":
            print("Running all tests")
        else:
            # All cb's take db_manager obj as a param
            test_func_cb = self.valid_tests[self.args['test']]
            test_func_cb(self.db_manager)

        # Close all connnections
        self.db_manager.cleanup()

if __name__ == '__main__':
    MainTester()


