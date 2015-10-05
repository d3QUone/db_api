__author__ = 'vladimir'

from flask import Flask
import ujson

from blueprints.database import FuckingCoolORM
from blueprints.forum import forum
from blueprints.post import post
from blueprints.user import user
from blueprints.thread import thread


BASE_URL = "/db/api"


app = Flask("db-api")
app.config["DEBUG"] = True

app.register_blueprint(forum, url_prefix=BASE_URL)
app.register_blueprint(post, url_prefix=BASE_URL)
app.register_blueprint(user, url_prefix=BASE_URL)
app.register_blueprint(thread, url_prefix=BASE_URL)


@app.route(BASE_URL + "/status", methods=["GET"])
def status():
    res = {
        "forum": FuckingCoolORM.Instance().get_count("forum_t"),
        "post": FuckingCoolORM.Instance().get_count("post_t"),
        "user": FuckingCoolORM.Instance().get_count("user_t"),
        "thread": FuckingCoolORM.Instance().get_count("thread_t"),
    }
    return ujson.dumps({"code": 0, "response": res})


def debug_printout():
    res = ""
    for i in app.url_map.iter_rules():
        res += "  {0}\n".format(i)
    return "Current routes:\n\n" + res + "\n" + "-"*50


if __name__ == "__main__":
    print debug_printout()
    app.run("127.0.0.1", port=8080)
