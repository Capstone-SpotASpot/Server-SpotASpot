import pymysql
from pymysql import connections, cursors


def _cleanup_test(conn: connections, cursor: cursors):
    pass

def test_add_user(conn: connections, cursor: cursors):
    print("Running test for add_user procedure")
    _cleanup_test(conn, cursor)


