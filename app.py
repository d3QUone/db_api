__author__ = 'vladimir'

from flask import Flask
import pymysql

from blueprints.forum import forum
from blueprints.post import post
from blueprints.user import user
from blueprints.thread import thread


BASE_URL = "/db/api"

'''
connection = pymysql.connect(
    host='localhost',
    user='user',
    password='passwd',
    db='db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
'''

app = Flask("db-api")
app.config["debug"] = True

app.register_blueprint(forum, url_prefix=BASE_URL)
app.register_blueprint(post, url_prefix=BASE_URL)
app.register_blueprint(user, url_prefix=BASE_URL)
app.register_blueprint(thread, url_prefix=BASE_URL)


def debug_printout():
    res = ""
    for i in app.url_map.iter_rules():
        res += "  {0}\n".format(i)
    return "Current routes:\n\n" + res + "\n" + "-"*50


if __name__ == "__main__":
    print debug_printout()
    app.run("127.0.0.1", port=8080)
