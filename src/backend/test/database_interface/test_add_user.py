import unittest
import pymysql
from pymysql.cursors import Cursor
from pymysql.connections import Connection

#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager


class TestAddUser(unittest.TestCase):
    @classmethod
    def setUpConn(cls, db_manager: DB_Manager):
        cls._db_manager = db_manager

    def test_add_user(self) -> bool:
        cls = self.__class__

        # print("\nRunning test for add_user procedure")
        did_pass = True
        first_name = "test_fname"
        last_name = "test_lname"
        username = "test_username"
        pwd = "test_pwd"
        filter_str = []
        filter_str.append(f"first_name = '{first_name}'")
        filter_str.append(f"AND last_name = '{last_name}'")
        filter_str.append(f"AND username = '{username}'")
        filter_str.append(f"AND user_password = '{pwd}'")

        did_pass &= cls._db_manager.add_user(
            first_name, last_name, username, pwd)
        # Check to see that there is a row in the table which matches the inputs
        try:
            filter_clause = " ".join(filter_str)
            cls._db_manager.cursor.execute(
                f"select * from users WHERE {filter_clause};")
        except:
            did_pass = False

        # Cleanup test by deleting the newly made row
        try:
            filter_clause = " ".join(filter_str[:-1])
            cls._db_manager.cursor.execute(
                f"DELETE FROM users WHERE {filter_clause};")
            cls._db_manager.conn.commit()
            res = cls._db_manager.cursor.fetchall()
        except:
            did_pass = False

        self.assertTrue(did_pass, "Failed to add user to database")
        return True
