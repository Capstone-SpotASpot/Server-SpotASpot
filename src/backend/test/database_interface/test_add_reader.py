from tkinter.tix import Tree
from db_manager import DB_Manager
from pymysql.cursors import Cursor
from pymysql import connections, cursors
import pymysql
from sre_constants import FAILURE


#--------------------------------Project Includes--------------------------------#


def test_add_reader(db_manager: DB_Manager) -> bool:
    # Fail case  - more than 6 digits after decimal place
    latitude = "42.337108"
    longitude = "-71.086593"
    filter_clause = f"latitude = '{latitude}' AND longitude = '{longitude}'"
    sql_count_expr = f"SELECT COUNT(*) FROM readers WHERE {filter_clause};"
    db_manager.cursor.execute(sql_count_expr)
    before_add_raw = db_manager.cursor.fetchall()
    count_before_addition = (list(before_add_raw[0].values()))[0]

    res = db_manager.add_reader(latitude, longitude)
    assert(res == True)


    # Check that the row is in the table correctly
    db_manager.cursor.execute(sql_count_expr)
    raw_count_after_addition = db_manager.cursor.fetchall()
    count_after_addition = (list(raw_count_after_addition[0].values()))[0]
    assert(count_after_addition == count_before_addition + 1)
    print("Testing add_reader with  OK coordinates....passed!")

    print("All add_reader tests passed!!!!")

    # Delete the entry from the table - the last one
    db_manager.cursor.execute("DELETE FROM readers ORDER BY reader_id desc limit 1")
    db_manager.conn.commit()

    return True
