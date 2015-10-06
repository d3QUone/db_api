__author__ = 'vladimir'

import pymysql

from . import safe_injection

try:
    connection = pymysql.connect(
        host='localhost',
        user='user',
        password='passwd',
        db='db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
except pymysql.err.OperationalError:
    connection = None
    print "Can't connect to DB, debug mode ON"


class BaseORM(object):
    connection = connection
    db_table = None
    base_url = None
    schema = None
    debug = True

    def table_exists(self):
        if not self.debug:
            with self.connection.cursor() as cursor:
                sql = """SHOW TABLES LIKE %s;"""
                cursor.execute(sql, (self.db_table,))
                result = cursor.fetchone()
                print "Is", self.db_table, "exists? - ", result, "\nLen =", len(result)
        else:
            return True

    def create_table(self):
        if not self.debug:
            with self.connection.cursor() as cursor:
                cursor.execute(self.schema)
                result = cursor.fetchone()
                print "Creating table", self.db_table, ":\n", result
        else:
            return True

    def drop_table(self):
        if not self.debug:
            with self.connection.cursor() as cursor:
                sql = """DROP TABLE %s;"""
                cursor.execute(sql, (self.db_table,))
                result = cursor.fetchone()
                print "Dropping table", self.db_table, ":\n", result
        return True

    def get_count(self):
        if not self.debug:
            with self.connection.cursor() as cursor:
                sql = """SELECT count(*) FROM %s;"""
                cursor.execute(sql, (self.db_table,))
                result = cursor.fetchone()
                return result
        else:
            return 123

    @safe_injection
    def test(self, data):
        print data

# TODO: think about migration mechanism (at least drop -> create)

# x = BaseORM()
# print x.test("test!")  # raises Exception
# print x.test({"key": "smth with ' inj", "data": "asjo12989", "name": "Vladimir", "last_name": "Oiaod\" or 1=1"})
