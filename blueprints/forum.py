__author__ = 'vladimir'

import ujson

from flask import Blueprint

from database import BaseORM, safe_injection


class ForumBase(BaseORM):
    db_table = "Forum_t"
    base_url = "/forum"
    schema = """
CREATE TABLE 'Forum_t' (
  'id' INT AUTO_INCREMENT,
  'short_name' VARCHAR(100) NOT NULL,
  'name' VARCHAR(100) NOT NULL,
  'user' VARCHAR(100) NOT NULL,
  'isDeleted' BOOLEAN DEFAULT TRUE,
  PRIMARY KEY('short_name')
);
"""

    @safe_injection
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

forum_manager = ForumBase()

forum_blueprint = Blueprint("forum", __name__)

@forum_blueprint.route(forum_manager.base_url + "/create", methods=["GET"])
def create():
    res = forum_manager.create({"key": "smth with ' inj", "data": "asjo12989", "name": "Vladimir", "last_name": "Oiaod\" or 1=1"})
    return ujson.dumps({"success": True})
