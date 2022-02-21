from pickle import TRUE
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

        created_reader_id = self.help_add_reader()

        # Delete the entry from the table
        self.help_remove_reader(created_reader_id)


        return True

    def test_add_reader_event(self) -> bool:
        cls = self.__class__

        # Setup the inputs
        timestamp = datetime.now()
        readeable_timestamp_in = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        singal_strength_in = 1
        reader_id = self.help_add_reader()
        tag_id = cls._db_manager.add_tag() # -1 on fail,

        # Call the function being tested
        id_dict = cls._db_manager.add_reader_event(
            readeable_timestamp_in, singal_strength_in, reader_id, tag_id)[0]
        observation_id = id_dict['created_observ_id']
        detection_id = id_dict['created_detect_id']

        # Verify the results
        # Check that the row's values are exactly correct
        cls._db_manager.cursor.execute(
            "SELECT * FROM observation_event WHERE observation_id = '%s'", observation_id)
        inserted_row = cls._db_manager.cursor.fetchone()

        add_observ_success = observation_id != None
        add_detection_and_park_car_success = detection_id != None

        # Delete the entry(s) from the table if they were added
        # do BEFORE asserting. So on failure, rows deleted before program closes
        if add_observ_success:
            cls._db_manager.cursor.execute(
                "DELETE FROM observation_event WHERE observation_id = '%s'", observation_id)
            cls._db_manager.conn.commit()
        if add_detection_and_park_car_success:
            cls._db_manager.cursor.execute(
                "DELETE FROM detects WHERE detection_id = '%s'", detection_id)
            cls._db_manager.conn.commit()
        if reader_id != -1:
            self.help_remove_reader(reader_id)
        if tag_id != -1:
            self.help_remove_tag(tag_id)

        # Perform all assertions after cleaup is done
        # Make sure adding was reported as successfull and the tuple truly exists in the table
        self.assertTrue(add_observ_success,
                        f"observation_id = {observation_id}. Cant be None")

        self.assertTrue(add_detection_and_park_car_success,
                        f"detection_id = {detection_id}. Cant be None")

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
        self.help_remove_tag(created_tag_id)


        return True

    ###### Helpers / Setup functions
    def help_add_reader(self) -> int:
        """Helper function to add a reader - and test that it was added correctly.
        Also performs testing. Useful for testing add_reader
        AND other tests that need to add a reader.
        \n:return The reader_id created. -1 on fail"""
        cls = self.__class__

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
        self.assertTrue(count_after_addition == count_before_addition + 1,
                        "The reader row was not succesfully added")

        return created_reader_id


    def help_remove_reader(self, reader_id):
        cls = self.__class__
        cls._db_manager.cursor.execute(f"DELETE FROM readers WHERE reader_id = {reader_id}")
        cls._db_manager.conn.commit()

    def help_remove_tag(self, tag_id) -> int:
        """Util function to add a tag. Remove the row from the tag with the id given.
        Also performs asserting during procedure calls"""
        cls = self.__class__

        cls._db_manager.cursor.execute(f"delete from tag where tag_id = {tag_id};")
        cls._db_manager.conn.commit()
