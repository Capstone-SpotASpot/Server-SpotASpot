import unittest
import pymysql
from pymysql.cursors import Cursor
from pymysql.connections import Connection

#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager


class TestUser(unittest.TestCase):
    @classmethod
    def setUpConn(cls, db_manager: DB_Manager):
        cls._db_manager = db_manager

    def test_add_user(self) -> bool:
        cls = self.__class__

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
            first_name, last_name, username, pwd) != -1
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

    def test_add_car(self) -> bool:
        """Test add_car() to make sure a new car id is returned and that it is unique"""
        cls = self.__class__

        # get cars table prior to testing
        cls._db_manager.cursor.execute("select * from registered_cars;")
        past_cars_table = list(cls._db_manager.cursor.fetchall())

        # create a test user (user needed to add a car)
        fake_user_id = cls._db_manager.add_user("fname", "lname", "uname", "pwd")
        if(fake_user_id == -1):
            # cleanup before exit
            cls._db_manager.cursor.execute(f"delete from users where user_id = {fake_user_id};")
            cls._db_manager.conn.commit()
        self.assertTrue(fake_user_id != -1, "Failed to add test user for add_car")

        # create tags for car (needed to add)
        front_tag = self._db_manager.add_tag()
        middle_tag = self._db_manager.add_tag()
        rear_tag = self._db_manager.add_tag()

        # RUN ACTUAL DB PROCEDURE
        # call add_car() -- returns -1 on error, car_id otherwise
        created_car_id = cls._db_manager.add_car(
            fake_user_id,
            front_tag,
            middle_tag,
            rear_tag
        )
        if(created_car_id == -1):
            # cleanup before exit
            cls._db_manager.cursor.execute(f"delete from users where user_id = {fake_user_id};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {front_tag};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {middle_tag};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {rear_tag};")
            cls._db_manager.conn.commit()
        self.assertTrue(created_car_id != -1, "Calling add_car Failed")


        # cleanup if exit needed
        def cleanup_car():
            cls._db_manager.cursor.execute(f"delete from users where user_id = {fake_user_id};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {front_tag};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {middle_tag};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from tag where tag_id = {rear_tag};")
            cls._db_manager.conn.commit()
            cls._db_manager.cursor.execute(f"delete from registered_cars where car_id = {created_car_id};")
            cls._db_manager.conn.commit()


        # Check that the row is in the table correctly
        is_car_id_unique = lambda id, table: list([dict["car_id"] for dict in table]).count(id) == 1
        cls._db_manager.cursor.execute("select * from registered_cars;")
        after_test_car_table = list(cls._db_manager.cursor.fetchall())

        did_car_table_grow = len(after_test_car_table) == len(past_cars_table)+1
        if(not did_car_table_grow): cleanup_car()
        self.assertTrue(did_car_table_grow, "add_car failed to grow car table")

        if(not is_car_id_unique(created_car_id, after_test_car_table)):
            cleanup_car()
        self.assertTrue(
            is_car_id_unique(created_car_id, after_test_car_table),
            "add_car(): car_id is not unique in table"
        )

        created_row = list(filter(lambda x: x["car_id"] == created_car_id, after_test_car_table))[0]
        if(created_row["front_tag"] == front_tag or
           created_row["middle_tag"] == middle_tag or
           created_row["rear_tag"] == rear_tag
        ): cleanup_car()
        self.assertTrue(
            created_row["front_tag"] == front_tag,
            "test_add_tag: Front tag does not match expected"
        )
        self.assertTrue(
            created_row["middle_tag"] == middle_tag,
            "test_add_tag: Middle tag does not match expected"
        )
        self.assertTrue(
            created_row["rear_tag"] == rear_tag,
            "test_add_tag: Rear tag does not match expected"
        )

        # remove trace of test from db by removing added rows
        # safe to use f-strings bc no user input
        cleanup_car()
