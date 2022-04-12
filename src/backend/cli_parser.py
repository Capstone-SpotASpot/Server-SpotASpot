import argparse # cli parsing
import getpass


class CLIParser():
    def __init__(self):
        """Class used to encapsulate all command line parsing.
        `.args` returns the arguments parsed.
        args = port, debugMode, db_user, pwd, db, db_host"""
        self._parser = argparse.ArgumentParser(description="Start up a web app GUI for the SpotASpot DB App")

        self._create_args()

        # Actually Parse Flags (turn into dictionary)
        self.args = vars(self._parser.parse_args())

        self._prompt_for_pwd()

    def _create_args(self):
        self._parser.add_argument(
            "-p", "--port",
            type=int,
            required=False,
            help="The port to run the web app from",
            default=31025
        )

        # defaults debugMode to false (only true if flag exists)
        self._parser.add_argument(
            "--debugModeOn",
            action="store_true",
            dest="debugMode",
            required=False,
            help="Use debug mode for development environments",
            default=False
        )
        self._parser.add_argument(
            "--debugModeOff",
            action="store_false",
            dest="debugMode",
            required=False,
            help="Dont use debug mode for production environments",
            default=True
        )

        self._parser.add_argument(
            "-db_u", "--db_username",
            required=False,
            # sometimes this is also root
            default="capstone",
            dest="db_user",
            help="The username for the Database"
        )

        self._parser.add_argument(
            "-pwd", "--password",
            required=False, # but if not provided asks for input
            default=None,
            dest="pwd",
            help="The password for the Database"
        )

        self._parser.add_argument(
            "-d", "--db",
            required=False,
            default="SpotASpot",
            dest="db",
            help="The name of the database to connect to"
        )

        self._parser.add_argument(
            "-dev", "--dev_db",
            required=False,
            action="store_const",
            const="SpotASpot_dev",
            dest="db",
            help="Sets the name of the database to connect to as the dev database"
        )

        self._parser.add_argument(
            "-dbh", "--database_host",
            required=False,
            default="localhost",
            dest="db_host",
            help="Set the host ip address of the database (can be localhost)"
        )

    def _prompt_for_pwd(self):
        """When the db pwd isnt input, prompts the user for it"""
        # ask for input if password not given
        if self.args["pwd"] == None:
            pass_msg = "Enter the password for user '"
            pass_msg += str(self.args["db_user"])
            pass_msg += "' for the database '"
            pass_msg += str(self.args["db"])
            pass_msg += "': "
            self.args["pwd"] = getpass.getpass(pass_msg)
