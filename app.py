__author__ = 'vladimir'

from flask import Flask
import pymysql


connection = pymysql.connect(
    host='localhost',
    user='user',
    password='passwd',
    db='db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


app = Flask("db-api")


if __name__ == "__main__":
    print "Init"
