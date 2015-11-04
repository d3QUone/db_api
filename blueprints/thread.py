__author__ = 'vladimir'

import ujson
from flask import Blueprint

from database import update_query, select_query


thread_blueprint = Blueprint("thread_blueprint", __name__, url_prefix="thread")


@thread_blueprint.route("/create/", methods=["POST"])
def create():
    return ujson.dumps({"success": True})
