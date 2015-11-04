__author__ = 'vladimir'

import ujson
from flask import Flask

from blueprints.database import update_query
from blueprints.forum import forum_blueprint
from blueprints.post import post_blueprint
from blueprints.user import user_blueprint
from blueprints.thread import thread_blueprint


app = Flask("db-api")
app.config["DEBUG"] = True
app.config["BASE_URL"] = "/db/api/"


for blueprint in [forum_blueprint, post_blueprint, user_blueprint, thread_blueprint]:
    app.register_blueprint(blueprint, url_prefix=app.config["BASE_URL"] + blueprint.url_prefix)


@app.route(app.config["BASE_URL"] + "/status", methods=["GET"])
def status():
    res = {
        "forum": 0,
        "post": 0,
        "user": 0,
        "thread_blueprint": 0,
    }
    return ujson.dumps({"code": 0, "response": res})


@app.route("/db/api/clear/", methods=["POST"])
def truncate_db():
    tables = ['post', 'thread', 'forum', 'subscription', 'follower', 'user']
    update_query("SET global foreign_key_checks = 0;")
    for table in tables:
        update_query("TRUNCATE TABLE `%s`;" % table)
    update_query("SET global foreign_key_checks = 1;")
    return ujson.dumps({"code": 0, "response": "OK"})


def debug_printout():
    res = ""
    for i in app.url_map.iter_rules():
        res += "  {0} | Methods = {1}\n".format(i, ", ".join(i.methods))
    print "Current routes:\n\n{0}\n".format(res), "-"*50


if __name__ == "__main__":
    debug_printout()
    app.run("127.0.0.1", port=5000)
