__author__ = 'vladimir'

import pymysql


def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='forumdb',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )


def update_query(query, params=None, verbose=False):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    row_id = cursor.lastrowid
    amount = cursor.rowcount
    cursor.close()
    connection.close()
    if verbose:
        print "Update Query: last-row-id = {0}, total {1} row(s) updated".format(row_id, amount)
    return row_id


def select_query(query, params=None, verbose=False):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    if verbose:
        print "Select Query: {0} row(s) were found, res = {1}".format(len(res), res)
    return res
