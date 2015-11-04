__author__ = 'vladimir'

import ujson
from flask import Blueprint, request

from database import update_query, select_query


forum_blueprint = Blueprint("forum", __name__, url_prefix="forum")


class ForumBase(object):
    db_table = "Forum_t"
    base_url = "/forum"
    schema = """
CREATE TABLE 'Forum_t' (
  'id' INT AUTO_INCREMENT UNIQUE,
  'short_name' VARCHAR(100) PRIMARY KEY,
  'name' VARCHAR(100) NOT NULL,
  'user' VARCHAR(100) NOT NULL,
  'isDeleted' BOOLEAN DEFAULT FALSE
  # PRIMARY KEY('short_name')
);
""".replace("'", "`")

    def create(self, data):
        print "Forum create...", data  # check injections
        name = data.get("name", None)
        short_name = data.get("short_name", None)
        user = data.get("user", None)
        try:
            with self.connection.cursor() as cursor:
                sql = """INSERT INTO %s () %s;"""
                cursor.execute(sql, (self.db_table,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print e
            return None

    def detail(self, data):
        short_name = data.get("short_name", None)
        try:
            with self.connection.cursor() as cursor:
                sql = """SELECT * FROM %s WHERE `short_name`=%s;"""
                cursor.execute(sql, (self.db_table, short_name, ))
                result = cursor.fetchone()
                return {
                    "status": 0,
                    "data": result
                }
        except Exception as e:
            return {
                "status": 1,  # ?
                "error": e
            }



@forum_blueprint.route("/create/", methods=["POST"])
def create():
    # res = forum_manager.create()
    return ujson.dumps({"success": True})


@forum_blueprint.route("/detail/", methods=["GET"])
def detail():
    params = {
        "short_name": request.args.get("forum", None),
        "related": request.args.get("related", []),
    }
    res = {}
    return ujson.dumps(res)
