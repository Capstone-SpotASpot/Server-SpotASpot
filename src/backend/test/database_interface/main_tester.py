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
from test_add_reader import test_add_reader

class MainTester(CLIParser):
    def __init__(self):
        """Basic class to setup testing sql files. Will handle establishing a connection to the test database"""
        self.valid_tests = {
            "ALL" : "ALL",
            "add_user": test_add_user,
            "add_reader": test_add_reader
        }

        # Init CLI first, then DBManager
        CLIParser.__init__(self, self.valid_tests)

        self.db_manager = DB_Manager(self.args['db_user'], self.args['pwd'],
                                self.args['db'], self.args['db_host'])
        self._did_all_pass = True

        if self.args['test'] == "ALL":
            print("Running all tests")
            del self.valid_tests["ALL"]
            for valid_test in self.valid_tests.keys():
                self._did_all_pass &= self.valid_tests[valid_test](self.db_manager)
                print("-------------------------------------\n")
        else:
            # All cb's take db_manager obj as a param
            test_func_cb = self.valid_tests[self.args['test']]
            self._did_all_pass &= test_func_cb(self.db_manager)

        # Close all connnections
        self.db_manager.cleanup()

        ret_code = "yes" if self._did_all_pass else "no"
        print(f"Did all tests pass, {ret_code}")

if __name__ == '__main__':
    MainTester()


