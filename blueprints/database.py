__author__ = 'vladimir'

import pymysql


def update_query(query, verbose=False):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='forumdb',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    row_id = cursor.lastrowid
    amount = cursor.rowcount
    cursor.close()
    connection.close()
    if verbose:
        print "Update Query: got row id = {0}, amount = {1}".format(row_id, amount)
    return row_id


def select_query(query, verbose=False):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='forumdb',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    if verbose:
        print "Select Query: {0} rows were found, res = {1}".format(len(res), res)
    return res
