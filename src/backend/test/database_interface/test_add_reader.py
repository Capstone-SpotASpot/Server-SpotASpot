from tkinter.tix import Tree
from db_manager import DB_Manager
from pymysql.cursors import Cursor
from pymysql import connections, cursors
import pymysql
from sre_constants import FAILURE


#--------------------------------Project Includes--------------------------------#


def test_add_reader(db_manager: DB_Manager) -> bool:
    # Fail case  - more than 6 digits after decimal place
    print("Testing add_reader with  long coordinates - Expect adding to fail")
    latitude = "42.33710861206055"
    longitude = "-71.08659362792969"
    res = db_manager.add_reader(latitude, longitude)
    assert(res, False)
    print("Testing add_reader with long coordinates.....passed!")

    print("Testing add_reader with OK coordinates - Expect adding to succeed")
    latitude = "42.33710861206055"
    longitude = "-71.08659362792969"
    res = db_manager.add_reader(latitude, longitude)
    assert(res, True)
    print("Testing add_reader with  OK coordinates....passed!")

    print("All add_reader tests passed!!!!")
    return True
