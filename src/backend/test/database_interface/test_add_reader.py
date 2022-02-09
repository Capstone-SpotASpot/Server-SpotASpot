import unittest
from pymysql.cursors import Cursor
from pymysql import connections, cursors
from sre_constants import FAILURE
from datetime import datetime

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
        # self.assertTrue(res, "Calling add_reader Failed")


        # Check that the row is in the table correctly
        cls._db_manager.cursor.execute(sql_count_expr)
        raw_count_after_addition = cls._db_manager.cursor.fetchall()
        count_after_addition = (list(raw_count_after_addition[0].values()))[0]
        # self.assertTrue(count_after_addition == count_before_addition + 1,
        #                 "The reader row was not succesfully added")

        # Delete the entry from the table - the last one
        cls._db_manager.cursor.execute("DELETE FROM readers ORDER BY reader_id desc limit 1")
        cls._db_manager.conn.commit()

        return True

    def test_add_observation_event(self) -> bool:
        """Tests the handling of adding an observation event."""
        cls = self.__class__

        # Create an observation event
        timestamp = datetime.now()
        readeable_timestamp_in = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        singal_strength_in = 1
        observation_id_dict = cls._db_manager.add_observation_event(readeable_timestamp_in, singal_strength_in)
        observation_id = list(observation_id_dict.values())[0]

        # Make sure adding was reported as successfull and the tuple truly exists in the table
        add_observ_success = observation_id != None
        self.assertTrue(add_observ_success,
                        f"observation_id = {observation_id}. Cant be None")

        # Check that the row's values are exactly correct
        cls._db_manager.cursor.execute("SELECT * FROM observation_event WHERE observation_id = %s", observation_id)
        inserted_row = cls._db_manager.cursor.fetchone()

        self.assertTrue(str(inserted_row['time_observed']) == readeable_timestamp_in,
                        "Found timestamp = {}, expected = {}".format(
                            inserted_row['time_observed'], readeable_timestamp_in
        ))

        self.assertTrue(inserted_row['signal_strength'] == singal_strength_in,
                        "singal_strength in table = {}, expected = {}".format(
                            inserted_row['signal_strength'], singal_strength_in
        ))

        # info should always start relevant when first inserted
        self.assertTrue(inserted_row['is_relevant'] == 1,
                        "is_relevant in table = {}, expected = 1 (True)".format(
                        inserted_row['is_relevant']
        ))

        # Delete the entry(s) from the table if they were added
        if add_observ_success:
            cls._db_manager.cursor.execute("DELETE FROM observation_event WHERE observation_id = '%s'", observation_id)
            cls._db_manager.conn.commit()

