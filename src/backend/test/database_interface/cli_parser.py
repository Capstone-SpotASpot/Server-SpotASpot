import argparse  # cli paths
import getpass
import typing
from typing import Dict

class CLIParser():
    def __init__(self, valid_test: Dict):
        """Class to make adding CLI flags easy for ALL test classes Via inherinting them"""
        self.parser = argparse.ArgumentParser(
            description="Start up a connection the SpotASpot_dev DB")

        test_name_msg = "Enter the name of the test to run (excluding .py). Enter 'ALL' to run all tests.\n"
        test_name_msg += f"Choices = {list(valid_test.keys())}"
        self.parser.add_argument(
            "-t", "--testfile_name",
            help=test_name_msg,
            type=str,
            dest="test",
            action="store",
            default="ALL",
            choices=list(valid_test.keys())
        )

        # defaults debugMode to false (only true if flag exists)
        self.parser.add_argument(
            "--debugModeOn",
            action="store_true",
            dest="debugMode",
            required=False,
            help="Use debug mode for development environments",
            default=False
        )
        self.parser.add_argument(
            "--debugModeOff",
            action="store_false",
            dest="debugMode",
            required=False,
            help="Dont use debug mode for production environments",
            default=True
        )

        self.parser.add_argument(
            "-db_u", "--db_username",
            required=False,
            # sometimes this is also root
            default="capstone",
            dest="db_user",
            help="The username for the Database"
        )

        self.parser.add_argument(
            "-pwd", "--password",
            required=False,  # but if not provided asks for input
            default=None,
            dest="pwd",
            help="The password for the Database"
        )

        # Assume the DB in question is the test database...bc this is testing
        self.parser.add_argument(
            "-d", "--db",
            required=False,
            default="SpotASpot_dev",
            dest="db",
            help="The name of the database to connect to"
        )

        self.parser.add_argument(
            "-dbh", "--database_host",
            required=False,
            default="localhost",
            dest="db_host",
            help="Set the host ip address of the database (can be localhost)"
        )

        # Actually Parse Flags (turn into dictionary)
        self.args = vars(self.parser.parse_args())

        # ask for input if password not given
        if self.args["pwd"] == None:
            pass_msg = "Enter the password for user '"
            pass_msg += str(self.args["db_user"])
            pass_msg += "' for the database '"
            pass_msg += str(self.args["db"])
            pass_msg += "': "
            self.args["pwd"] = getpass.getpass(pass_msg)
