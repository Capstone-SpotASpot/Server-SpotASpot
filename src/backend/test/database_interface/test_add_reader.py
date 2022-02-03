import unittest
from pymysql.cursors import Cursor
from pymysql import connections, cursors
from sre_constants import FAILURE


#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager


class TestAddReader(unittest.TestCase):
    @classmethod
    def setUpConn(cls, db_manager: DB_Manager):
        cls._db_manager = db_manager

    def test_add_reader(self) -> bool:
        cls = self.__class__

        # Fail case  - more than 6 digits after decimal place
        latitude = "42.337108"
        longitude = "-71.086593"
        filter_clause = f"latitude = '{latitude}' AND longitude = '{longitude}'"
        sql_count_expr = f"SELECT COUNT(*) FROM readers WHERE {filter_clause};"
        cls._db_manager.cursor.execute(sql_count_expr)
        before_add_raw = cls._db_manager.cursor.fetchall()
        count_before_addition = (list(before_add_raw[0].values()))[0]

        res = cls._db_manager.add_reader(latitude, longitude)
        self.assertTrue(res, "Calling add_reader Failed")


        # Check that the row is in the table correctly
        cls._db_manager.cursor.execute(sql_count_expr)
        raw_count_after_addition = cls._db_manager.cursor.fetchall()
        count_after_addition = (list(raw_count_after_addition[0].values()))[0]
        self.assertTrue(count_after_addition == count_before_addition + 1,
                        "The reader row was not succesfully added")

        # Delete the entry from the table - the last one
        cls._db_manager.cursor.execute("DELETE FROM readers ORDER BY reader_id desc limit 1")
        cls._db_manager.conn.commit()

        return True
