import unittest
from pymysql.cursors import Cursor
from pymysql import connections, cursors
from sre_constants import FAILURE
from datetime import datetime

#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager


class TestReader(unittest.TestCase):
    @classmethod
    def setUpConn(cls, db_manager: DB_Manager):
        cls._db_manager = db_manager

    def test_add_reader(self) -> bool:
        cls = self.__class__

        # Fail case  - more than 6 digits after decimal place
        latitude = "42.337108"
        longitude = "-71.086593"
        reader_range = 20.0
        filter_clause = f"latitude = '{latitude}' AND longitude = '{longitude}'"
        sql_count_expr = f"SELECT COUNT(*) FROM readers WHERE {filter_clause};"
        cls._db_manager.cursor.execute(sql_count_expr)
        before_add_raw = cls._db_manager.cursor.fetchall()
        count_before_addition = (list(before_add_raw[0].values()))[0]

        created_reader_id = cls._db_manager.add_reader(latitude, longitude, reader_range)
        self.assertTrue(created_reader_id != -1, "Calling add_reader Failed")


        # Check that the row is in the table correctly
        cls._db_manager.cursor.execute(sql_count_expr)
        raw_count_after_addition = cls._db_manager.cursor.fetchall()
        count_after_addition = (list(raw_count_after_addition[0].values()))[0]
        # self.assertTrue(count_after_addition == count_before_addition + 1,
        #                 "The reader row was not succesfully added")

        # Delete the entry from the table - the last one
        # safe to use f-strings bc no user input
        cls._db_manager.cursor.execute(f"DELETE FROM readers WHERE reader_id = {created_reader_id}")
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

    def test_add_tag(self) -> bool:
        """Test add_tag() to make sure a new tag id is returned and that it is unique"""
        cls = self.__class__

        def get_curr_tag_ids():
            # get all currently existing tag ids
            cls._db_manager.cursor.execute("select tag_id from tag;")
            query_raw_results = cls._db_manager.cursor.fetchall()
            # flatten list of dicts into list of tag ids
            return [res_dict["tag_id"] for res_dict in query_raw_results]

        # get tag ids prior to testing
        past_tag_ids = get_curr_tag_ids()

        # call add_tag() -- returns -1 on error, tag_id otherwise
        created_tag_id = cls._db_manager.add_tag()
        self.assertTrue(created_tag_id != -1, "Calling add_tag Failed")

        # make sure the new tag id is unique from past
        self.assertTrue(created_tag_id not in past_tag_ids, "add_tag created bad new tag id")

        # Check that the row is in the table correctly
        after_test_tag_ids = get_curr_tag_ids()
        self.assertTrue(len(after_test_tag_ids) == len(past_tag_ids)+1, "add_tag failed to insert new tag entry")
        self.assertTrue(created_tag_id in after_test_tag_ids, "add_tag failed to insert new tag id in new entry")
        cls._db_manager.cursor.execute("select tag_id from tag;")

        # remove trace of test from db by removing added tag (the last one)
        # safe to use f-strings bc no user input
        cls._db_manager.cursor.execute(f"delete from tag where tag_id = {created_tag_id};")
        cls._db_manager.conn.commit()
