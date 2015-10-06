__author__ = 'vladimir'

from flask import Flask
import ujson

from blueprints.forum import forum_blueprint, forum_manager
from blueprints.post import post_blueprint, post_manager
from blueprints.user import user_blueprint, user_manager
from blueprints.thread import thread_blueprint, thread_manager


BASE_URL = "/db/api"

app = Flask("db-api")
app.config["DEBUG"] = True

for blueprint in [forum_blueprint, post_blueprint, user_blueprint, thread_blueprint]:
    app.register_blueprint(blueprint, url_prefix=BASE_URL)


@app.before_first_request
def init_database():
    for manager in [forum_manager, post_manager, user_manager, thread_manager]:
        if not manager.table_exists():
            print "* creating table", manager.db_table
            manager.create_table()


@app.route(BASE_URL + "/status", methods=["GET"])
def status():
    res = {
        "forum": forum_manager.get_count(),
        "post": post_manager.get_count(),
        "user": user_manager.get_count(),
        "thread_blueprint": thread_manager.get_count(),
    }
    return ujson.dumps({"code": 0, "response": res})


def debug_printout():
    res = ""
    for i in app.url_map.iter_rules():
        res += "  {0} | Methods = {1}\n".format(i, ", ".join(i.methods))
    return "Current routes:\n\n" + res + "\n" + "-"*50


if __name__ == "__main__":
    print debug_printout()
    app.run("127.0.0.1", port=8080)
