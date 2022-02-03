from sre_constants import FAILURE
import pymysql
from pymysql import connections, cursors
from pymysql.cursors import Cursor


#--------------------------------Project Includes--------------------------------#
from db_manager import DB_Manager

def test_add_user(db_manager: DB_Manager) -> bool:
    print("\nRunning test for add_user procedure")
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

    did_pass &= db_manager.add_user(first_name, last_name, username, pwd)
    # Check to see that there is a row in the table which matches the inputs
    try:
        filter_clause = " ".join(filter_str)
        db_manager.cursor.execute(f"select * from users WHERE {filter_clause};")
    except:
        did_pass = False

    # Cleanup test by deleting the newly made row
    try:
        filter_clause = " ".join(filter_str[:-1])
        db_manager.cursor.execute(f"DELETE FROM users WHERE {filter_clause};")
        db_manager.conn.commit()
        res = db_manager.cursor.fetchall()
    except:
        did_pass = False

    assert(did_pass)
    print("test_add_user.........passed!")



