__author__ = 'vladimir'

import pymysql


# TODO: do as decorator
def safe_injection(string):
    """
    remove " ' etc ...
    """
    return string


# 'Singleton' stolen from http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.
    """
    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class FuckingCoolORM(object):

    def __init__(self):
        # self.connection = pymysql.connect(
        #     host='localhost',
        #     user='user',
        #     password='passwd',
        #     db='db',
        #     charset='utf8mb4',
        #     cursorclass=pymysql.cursors.DictCursor
        # )
        pass

    def get_count(self, db_table):
        # with self.connection.cursor() as cursor:
        #     sql = """SELECT count(*) FROM %s;"""
        #     cursor.execute(sql, (db_table,))
        #     result = cursor.fetchone()
        #     return result
        return 123
